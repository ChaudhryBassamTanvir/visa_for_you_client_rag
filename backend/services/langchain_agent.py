# services/langchain_agent.py

import os
import requests
import resend
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.messages import HumanMessage
from slack_sdk import WebClient
from db.database import create_appointment, get_or_create_client
from services.rag_engine import get_relevant_context
from datetime import datetime, date

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=os.getenv("GEMINI_API_KEY")
)

conversation_history: dict = {}
client_info: dict           = {}

# ── Idempotency: track processed message IDs (WhatsApp / Slack) ──
_processed_ids: set[str] = set()

def is_duplicate_message(msg_id: str) -> bool:
    if msg_id in _processed_ids:
        return True
    _processed_ids.add(msg_id)
    if len(_processed_ids) > 20_000:
        oldest = next(iter(_processed_ids))
        _processed_ids.discard(oldest)
    return False

def store_slack_id(user_id: str, slack_user_id: str):
    if user_id not in client_info:
        client_info[user_id] = {}
    client_info[user_id]["slack_user_id"] = slack_user_id

def today_str() -> str:
    """Return today as DD/MM/YYYY so the LLM always knows the current date."""
    return date.today().strftime("%d/%m/%Y")

# ============================
# 🔧 TRELLO
# ============================
TRELLO_TODO_LIST_ID = os.getenv("TRELLO_LIST_ID", "69ce483fd98acbd8128e9d9c")

def create_trello_card(title: str, description: str = "") -> str:
    url    = "https://api.trello.com/1/cards"
    params = {
        "key":    os.getenv("TRELLO_API_KEY"),
        "token":  os.getenv("TRELLO_TOKEN"),
        "idList": TRELLO_TODO_LIST_ID,
        "name":   title,
        "desc":   description
    }
    response = requests.post(url, params=params)
    return response.json().get("shortUrl", "")

# ============================
# 📧 EMAIL  (send to ADMIN)
# ============================
def send_email_notification(subject: str, client: dict, details: dict, card_url: str):
    resend.api_key = os.getenv("RESEND_API_KEY")
    now = datetime.now().strftime("%B %d, %Y at %I:%M %p")

    rows = "".join(
        f'<tr><td style="padding:8px 16px;font-size:12px;color:#999;width:140px;border-bottom:1px solid #f0f0f0">{k}</td>'
        f'<td style="padding:8px 16px;font-size:14px;color:#1a1a1a;border-bottom:1px solid #f0f0f0">{v}</td></tr>'
        for k, v in details.items() if v
    )

    html = f"""
    <body style="font-family:Arial,sans-serif;background:#f4f4f0;padding:40px 0;">
      <table width="600" style="margin:auto;background:#fff;border-radius:12px;overflow:hidden;border:1px solid #e8e8e6;">
        <tr><td style="background:#1a1a1a;padding:28px 36px;">
          <p style="margin:0;font-size:11px;color:#888;letter-spacing:2px;text-transform:uppercase">Visa For You</p>
          <h1 style="margin:8px 0 0;font-size:20px;font-weight:500;color:#fff;">{subject}</h1>
          <p style="margin:4px 0 0;font-size:13px;color:#888;">{now}</p>
        </td></tr>
        <tr><td style="padding:28px 36px;">
          <p style="margin:0 0 12px;font-size:11px;color:#999;letter-spacing:1.5px;text-transform:uppercase;font-weight:500;">Client Information</p>
          <table width="100%" style="border:1px solid #e8e8e6;border-radius:8px;overflow:hidden;margin-bottom:24px;">
            <tr style="background:#f9f9f8;">
              <td style="padding:8px 16px;font-size:12px;color:#999;width:140px;border-bottom:1px solid #f0f0f0">Name</td>
              <td style="padding:8px 16px;font-size:14px;font-weight:500;border-bottom:1px solid #f0f0f0">{client.get('name','')}</td>
            </tr>
            <tr>
              <td style="padding:8px 16px;font-size:12px;color:#999;border-bottom:1px solid #f0f0f0">Email</td>
              <td style="padding:8px 16px;font-size:14px;border-bottom:1px solid #f0f0f0">{client.get('email','')}</td>
            </tr>
            <tr style="background:#f9f9f8;">
              <td style="padding:8px 16px;font-size:12px;color:#999;border-bottom:1px solid #f0f0f0">Phone</td>
              <td style="padding:8px 16px;font-size:14px;border-bottom:1px solid #f0f0f0">{client.get('phone','')}</td>
            </tr>
            <tr>
              <td style="padding:8px 16px;font-size:12px;color:#999">Channel</td>
              <td style="padding:8px 16px;font-size:14px;text-transform:capitalize">{client.get('channel','')}</td>
            </tr>
          </table>
          <p style="margin:0 0 12px;font-size:11px;color:#999;letter-spacing:1.5px;text-transform:uppercase;font-weight:500;">Appointment Details</p>
          <table width="100%" style="border:1px solid #e8e8e6;border-radius:8px;overflow:hidden;margin-bottom:24px;">
            {rows}
          </table>
          {"<a href='" + card_url + "' style='display:inline-block;padding:11px 24px;background:#1a1a1a;color:#fff;border-radius:8px;text-decoration:none;font-size:13px;font-weight:500;'>View on Trello →</a>" if card_url else ""}
        </td></tr>
        <tr><td style="padding:20px 36px;border-top:1px solid #f0f0f0;background:#f9f9f8;">
          <p style="margin:0;font-size:12px;color:#bbb;">Visa For You Consultancy — Automated Notification System</p>
        </td></tr>
      </table>
    </body>
    """
    try:
        resend.Emails.send({
            "from":    "Visa For You <onboarding@resend.dev>",
            "to":      os.getenv("NOTIFY_EMAIL"),
            "subject": f"🎓 {subject} — {client.get('name', '')}",
            "html":    html
        })
        print("✅ Admin email sent")
    except Exception as e:
        print(f"❌ Email error: {e}")


def send_client_confirmation_email(client: dict, details: dict):
    """Send confirmation email to the CLIENT (not admin)."""
    if not client.get("email"):
        print("⚠️  No client email — skipping client confirmation")
        return

    resend.api_key = os.getenv("RESEND_API_KEY")

    rows = "".join(
        f'<tr><td style="padding:8px 16px;font-size:12px;color:#999;width:160px;border-bottom:1px solid #f0f0f0">{k}</td>'
        f'<td style="padding:8px 16px;font-size:14px;color:#1a1a1a;border-bottom:1px solid #f0f0f0">{v}</td></tr>'
        for k, v in details.items() if v
    )

    html = f"""
    <body style="font-family:Arial,sans-serif;background:#f4f4f0;padding:40px 0;">
      <table width="600" style="margin:auto;background:#fff;border-radius:12px;overflow:hidden;border:1px solid #e8e8e6;">
        <tr><td style="background:#1a1a1a;padding:28px 36px;">
          <p style="margin:0;font-size:11px;color:#888;letter-spacing:2px;text-transform:uppercase">Visa For You</p>
          <h1 style="margin:8px 0 0;font-size:20px;font-weight:500;color:#fff;">Appointment Confirmed ✓</h1>
        </td></tr>
        <tr><td style="padding:28px 36px;">
          <p style="margin:0 0 6px;font-size:22px;font-weight:600;color:#111;letter-spacing:-0.3px;">
            Hi {client.get('name', '')},
          </p>
          <p style="margin:0 0 24px;font-size:14px;color:#888;">
            Your consultation with Visa For You has been confirmed. Here are your booking details:
          </p>
          <table width="100%" style="border:1px solid #e8e8e6;border-radius:8px;overflow:hidden;margin-bottom:28px;">
            {rows}
          </table>
          <p style="font-size:13px;color:#888;margin:0;">
            Our consultant will reach out to you before the appointment. If you need to reschedule,
            reply to this email or WhatsApp us directly.
          </p>
        </td></tr>
        <tr><td style="padding:20px 36px;border-top:1px solid #f0f0f0;background:#f9f9f8;">
          <p style="margin:0;font-size:12px;color:#bbb;">Visa For You · team@dstech.pk</p>
        </td></tr>
      </table>
    </body>
    """
    try:
        resend.Emails.send({
            "from":    "Visa For You <onboarding@resend.dev>",
            "to":      client["email"],
            "subject": f"Your Appointment is Confirmed — Visa For You",
            "html":    html
        })
        print(f"✅ Client confirmation email sent to {client['email']}")
    except Exception as e:
        print(f"❌ Client email error: {e}")


# ============================
# 🔔 SLACK TEAM NOTIFICATION
# ============================
def notify_slack_team(title: str, client: dict, details: dict, card_url: str):
    slack_client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
    channel      = os.getenv("SLACK_TEAM_CHANNEL", "#general")
    detail_text  = "\n".join(f"• *{k}:* {v}" for k, v in details.items() if v)
    try:
        slack_client.chat_postMessage(
            channel=channel,
            text=(
                f"🎓 *{title}*\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 *Name:* {client.get('name')}\n"
                f"📧 *Email:* {client.get('email')}\n"
                f"📞 *Phone:* {client.get('phone')}\n"
                f"📡 *Channel:* {client.get('channel')}\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"{detail_text}\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"🔗 *Trello:* {card_url}"
            )
        )
        print("✅ Slack team notified")
    except Exception as e:
        print(f"❌ Slack error: {e}")

# ============================
# 🛠️ TOOLS
# ============================

@tool
def save_client_info(name: str, email: str, phone: str, cgpa: str, degree: str, user_id: str) -> str:
    """
    Call this as soon as student provides their name, email, phone, CGPA and last degree.
    IMPORTANT: 'name' must be the person's actual full name only — never a country, city, budget,
    or university name. Extract only the human name from phrases like 'my name is X' or 'I am X'.
    user_id: pass the current user_id
    """
    client_info[user_id] = {
        **client_info.get(user_id, {}),
        "name":   name,
        "email":  email,
        "phone":  phone,
        "cgpa":   cgpa,
        "degree": degree,
    }
    print(f"✅ Student info saved: name={name}, CGPA={cgpa}, Degree={degree}")
    return (
        f"Thank you {name}! Based on your CGPA of {cgpa} and {degree} degree, "
        f"I can suggest the best study abroad options. "
        f"What is your target field of study, and what is your annual budget in USD?"
    )

@tool
def suggest_countries(budget_usd: str, target_field: str, user_id: str) -> str:
    """
    Call this after getting budget and target field of study.
    Suggest countries based on CGPA and budget using the knowledge base.
    user_id: pass the current user_id
    """
    info  = client_info.get(user_id, {})
    cgpa  = float(info.get("cgpa", "0") or "0")
    client_info[user_id]["budget"]       = budget_usd
    client_info[user_id]["target_field"] = target_field

    query   = f"study abroad CGPA {cgpa} budget {budget_usd} USD {target_field}"
    context = get_relevant_context(query)

    if cgpa >= 3.5:
        primary = ["UK", "USA", "Germany", "Canada", "Australia"]
        note    = "With your excellent CGPA, you qualify for top universities and scholarships worldwide!"
    elif cgpa >= 3.0:
        primary = ["Canada", "Australia", "Germany", "UK", "Malaysia"]
        note    = "Your CGPA opens doors to great universities in multiple countries!"
    elif cgpa >= 2.5:
        primary = ["Canada", "Australia", "Malaysia", "China"]
        note    = "There are excellent opportunities available for you!"
    else:
        primary = ["Malaysia", "China"]
        note    = "Malaysia and China offer affordable quality education with your profile."

    client_info[user_id]["suggested_countries"] = primary
    return (
        f"Based on your profile (CGPA: {cgpa}, Budget: ${budget_usd}/year, Field: {target_field}),\n"
        f"here are my top recommendations:\n\n"
        f"Recommended Countries: {', '.join(primary)}\n\n"
        f"{note}\n\n"
        f"Knowledge Base:\n{context[:600]}\n\n"
        f"Would you like to book a free consultation with our advisor, "
        f"or shall I provide more details about any specific country?"
    )

@tool
def book_appointment(preferred_date: str, preferred_time: str, purpose: str, user_id: str) -> str:
    """
    Call this when student wants to book an appointment with a consultant.
    preferred_date: resolve relative dates like 'tomorrow' against today = {today}.
    preferred_time: e.g. 2:00 PM
    purpose: reason for appointment
    user_id: pass the current user_id
    IMPORTANT: call this tool ONCE only — do not repeat the booking call.
    """.format(today=today_str())

    info      = client_info.get(user_id, {})
    name      = info.get("name", "Unknown")
    email     = info.get("email", "")
    phone     = info.get("phone", "")
    cgpa      = info.get("cgpa", "")
    degree    = info.get("degree", "")
    budget    = info.get("budget", "")
    channel   = info.get("channel", "web")
    countries = ", ".join(info.get("suggested_countries", []))

    # ── Guard: only book once per session ─────────────────────
    if client_info[user_id].get("appointment_booked"):
        return (
            f"Your appointment on {preferred_date} at {preferred_time} is already confirmed. "
            f"Is there anything else I can help you with?"
        )
    client_info[user_id]["appointment_booked"] = True

    # ── Save client to DB ──────────────────────────────────────
    client_id = get_or_create_client(
        name=name, channel=channel, phone=phone, email=email,
        slack_id=info.get("slack_user_id", "")
    )

    # ── Create Trello card ─────────────────────────────────────
    trello_desc = (
        f"Student: {name}\n"
        f"Email: {email}\n"
        f"Phone: {phone}\n"
        f"Channel: {channel}\n"
        f"CGPA: {cgpa}\n"
        f"Degree: {degree}\n"
        f"Budget: ${budget}/year\n"
        f"Interested Countries: {countries}\n\n"
        f"Appointment Date: {preferred_date}\n"
        f"Appointment Time: {preferred_time}\n"
        f"Purpose: {purpose}"
    )
    card_url = create_trello_card(
        f"Appointment: {name} — {preferred_date} {preferred_time}",
        trello_desc
    )

    # ── Save appointment to DB ─────────────────────────────────
    create_appointment(
        client_name=name, client_email=email, client_phone=phone,
        preferred_date=preferred_date, preferred_time=preferred_time,
        purpose=purpose, trello_url=card_url, client_id=client_id
    )

    # ── Notifications ──────────────────────────────────────────
    client_dict  = {"name": name, "email": email, "phone": phone, "channel": channel}
    details_dict = {
        "CGPA":                 cgpa,
        "Last Degree":          degree,
        "Budget per year":      f"${budget}" if budget else "",
        "Interested Countries": countries,
        "Appointment Date":     preferred_date,
        "Appointment Time":     preferred_time,
        "Purpose":              purpose,
    }

    # Admin email + Slack
    send_email_notification("New Appointment Booked", client_dict, details_dict, card_url)
    notify_slack_team("New Appointment — Visa For You", client_dict, details_dict, card_url)

    # Client confirmation email
    send_client_confirmation_email(client_dict, {
        "Date":    preferred_date,
        "Time":    preferred_time,
        "Purpose": purpose,
        "CGPA":    cgpa,
        "Degree":  degree,
    })

    return (
        f"Your appointment is confirmed, {name}!\n\n"
        f"Date: {preferred_date}\n"
        f"Time: {preferred_time}\n"
        f"Purpose: {purpose}\n\n"
        f"A confirmation email has been sent to {email}.\n"
        f"Our consultant will contact you shortly. Good luck with your study abroad journey!"
    )

@tool
def get_country_info(country: str, user_id: str) -> str:
    """
    Use this when student asks about a specific country, visa process,
    scholarships, requirements, or costs.
    user_id: pass the current user_id
    """
    context = get_relevant_context(f"{country} study abroad requirements visa scholarships tuition")
    return f"Here's detailed information about studying in {country}:\n\n{context}"

tools = [save_client_info, suggest_countries, book_appointment, get_country_info]

# ============================
# 🤖 AGENT  (system prompt injects today's date)
# ============================
def build_system_prompt() -> str:
    return f"""You are a warm and professional study abroad consultant at "Visa For You".
Today's date is {today_str()}.

## Conversation Flow:
1. Greet the student warmly and introduce yourself
2. Collect in order, ONE question at a time:
   - Full name  ← ONLY the person's name. Never use a country, city, budget amount, or
                  university name as the name. Extract ONLY from phrases like "my name is X"
                  or "I am X". Example: "Hi, Germany budget flexible my name is Hanan" → name = "Hanan"
   - Email address
   - Phone number
   - Last completed degree
   - CGPA
3. Once all five collected → call save_client_info immediately (with the correct name)
4. Ask about target field of study and annual budget
5. Call suggest_countries with budget and field
6. Answer questions about specific countries using get_country_info
7. When student wants appointment → collect preferred date and time (use today = {today_str()} to
   resolve "tomorrow" or relative dates) → call book_appointment EXACTLY ONCE

## Rules:
- Always pass user_id to every tool call
- Ask ONE question at a time — never ask two things in one message
- Never ask for information already provided in this conversation
- Call book_appointment ONCE — do not repeat it even if the student repeats themselves
- Be encouraging — every student has options!
- Sign off as "Visa For You Consultant" """

def get_agent_executor(user_id: str) -> AgentExecutor:
    """Return a fresh AgentExecutor with today's date baked into the system prompt."""
    from langchain import hub
    from langchain.agents import create_tool_calling_agent
    prompt = hub.pull("hwchase17/openai-tools-agent")
    agent  = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=False, max_iterations=6)

# ============================
# 🚀 RUN WITH MEMORY
# ============================
def run_agent(
    message:    str,
    user_id:    str,
    channel:    str = "web",
    message_id: str | None = None,
) -> str:
    """
    Args:
        message    : raw user text
        user_id    : unique per-user key (phone / slack_id / JWT sub)
        channel    : "whatsapp" | "slack" | "web"
        message_id : optional dedup key — WhatsApp message ID, Slack ts, etc.
    """
    # ── Dedup guard ────────────────────────────────────────────
    if message_id and is_duplicate_message(f"{user_id}:{message_id}"):
        print(f"⚠️  Duplicate message {message_id} for {user_id} — dropping")
        return ""

    if user_id not in client_info:
        client_info[user_id] = {}
    client_info[user_id]["channel"] = channel

    if user_id not in conversation_history:
        conversation_history[user_id] = []

    conversation_history[user_id].append(HumanMessage(content=message))

    executor = get_agent_executor(user_id)
    result   = executor.invoke({
        "messages": conversation_history[user_id],
        "input":    message,
        "system":   build_system_prompt(),    # fresh date on every call
    })

    conversation_history[user_id] = result.get("messages", conversation_history[user_id])
    output = result.get("output", "")

    if isinstance(output, list):
        output = " ".join(
            b.get("text", "") if isinstance(b, dict) else str(b)
            for b in output
        )
    return str(output).strip()