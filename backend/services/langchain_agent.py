# services/langchain_agent.py (Visa For You version)

import os
import requests
import resend
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from slack_sdk import WebClient
from db.database import create_appointment, get_or_create_client
from services.rag_engine import get_relevant_context
from datetime import datetime

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview",
    google_api_key=os.getenv("GEMINI_API_KEY")
)

conversation_history = {}
client_info = {}

def store_slack_id(user_id: str, slack_user_id: str):
    if user_id not in client_info:
        client_info[user_id] = {}
    client_info[user_id]["slack_user_id"] = slack_user_id

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
# 📧 EMAIL
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
          <p style="margin:0 0 12px;font-size:11px;color:#999;letter-spacing:1.5px;text-transform:uppercase;font-weight:500;">Details</p>
          <table width="100%" style="border:1px solid #e8e8e6;border-radius:8px;overflow:hidden;margin-bottom:24px;">
            {rows}
          </table>
          <a href="{card_url}" style="display:inline-block;padding:11px 24px;background:#1a1a1a;color:#fff;border-radius:8px;text-decoration:none;font-size:13px;font-weight:500;">View on Trello →</a>
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
        print("✅ Email sent")
    except Exception as e:
        print(f"❌ Email error: {e}")

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
    print(f"✅ Student info saved: {name}, CGPA: {cgpa}, Degree: {degree}")
    return f"Thank you {name}! Based on your CGPA of {cgpa} and {degree} degree, I can suggest the best study abroad options for you. What is your target budget per year in USD?"

@tool
def suggest_countries(budget_usd: str, target_field: str, user_id: str) -> str:
    """
    Call this after getting budget and target field of study.
    Suggest countries based on CGPA and budget using knowledge base.
    user_id: pass the current user_id
    """
    info   = client_info.get(user_id, {})
    cgpa   = float(info.get("cgpa", "0") or "0")
    client_info[user_id]["budget"]       = budget_usd
    client_info[user_id]["target_field"] = target_field

    # Get RAG context
    query   = f"study abroad CGPA {cgpa} budget {budget_usd} USD {target_field}"
    context = get_relevant_context(query)

    # Build suggestion based on CGPA
    if cgpa >= 3.5:
        primary   = ["UK", "USA", "Germany", "Canada", "Australia"]
        note      = "With your excellent CGPA, you qualify for top universities and scholarships worldwide!"
    elif cgpa >= 3.0:
        primary   = ["Canada", "Australia", "Germany", "UK", "Malaysia"]
        note      = "Your CGPA opens doors to great universities in multiple countries!"
    elif cgpa >= 2.5:
        primary   = ["Canada", "Australia", "Malaysia", "China"]
        note      = "There are excellent opportunities available for you!"
    else:
        primary   = ["Malaysia", "China"]
        note      = "Malaysia and China offer affordable quality education with your profile."

    client_info[user_id]["suggested_countries"] = primary
    return (
        f"Based on your profile (CGPA: {cgpa}, Budget: ${budget_usd}/year, Field: {target_field}),\n"
        f"here are my top recommendations:\n\n"
        f"🌍 *Recommended Countries:* {', '.join(primary)}\n\n"
        f"{note}\n\n"
        f"📚 *Knowledge Base Info:*\n{context[:600]}\n\n"
        f"Would you like to book a free consultation with our advisor to discuss this further? "
        f"Or shall I provide more details about any specific country?"
    )

@tool
def book_appointment(preferred_date: str, preferred_time: str, purpose: str, user_id: str) -> str:
    """
    Call this when student wants to book an appointment with a consultant.
    preferred_date: e.g. April 20, 2026
    preferred_time: e.g. 2:00 PM
    purpose: reason for appointment
    user_id: pass the current user_id
    """
    info    = client_info.get(user_id, {})
    name    = info.get("name", "Unknown")
    email   = info.get("email", "")
    phone   = info.get("phone", "")
    cgpa    = info.get("cgpa", "")
    degree  = info.get("degree", "")
    budget  = info.get("budget", "")
    channel = info.get("channel", "web")
    countries = ", ".join(info.get("suggested_countries", []))

    # Save client to DB
    client_id = get_or_create_client(
        name=name, channel=channel, phone=phone, email=email,
        slack_id=info.get("slack_user_id", "")
    )

    # Create Trello card
    trello_desc = (
        f"👤 Student: {name}\n"
        f"📧 Email: {email}\n"
        f"📞 Phone: {phone}\n"
        f"📡 Channel: {channel}\n"
        f"🎓 CGPA: {cgpa}\n"
        f"📚 Degree: {degree}\n"
        f"💰 Budget: ${budget}/year\n"
        f"🌍 Interested Countries: {countries}\n\n"
        f"📅 Appointment Date: {preferred_date}\n"
        f"🕐 Appointment Time: {preferred_time}\n"
        f"📋 Purpose: {purpose}"
    )
    card_url = create_trello_card(
        f"Appointment: {name} — {preferred_date} {preferred_time}",
        trello_desc
    )

    # Save to DB
    create_appointment(
        client_name=name, client_email=email, client_phone=phone,
        preferred_date=preferred_date, preferred_time=preferred_time,
        purpose=purpose, trello_url=card_url, db_user_id = get_or_create_client(
      name=name,
      channel=channel,
      phone=phone,
      email=email,
      slack_id=info.get("slack_user_id", "")
                )
    )

    # Email notification
    client_dict  = {"name": name, "email": email, "phone": phone, "channel": channel}
    details_dict = {
        "CGPA":               cgpa,
        "Last Degree":        degree,
        "Budget per year":    f"${budget}",
        "Interested Countries": countries,
        "Appointment Date":   preferred_date,
        "Appointment Time":   preferred_time,
        "Purpose":            purpose,
    }
    send_email_notification("New Appointment Booked", client_dict, details_dict, card_url)
    notify_slack_team("New Appointment — Visa For You", client_dict, details_dict, card_url)

    return (
        f"✅ Your appointment is confirmed, {name}!\n\n"
        f"📅 Date: {preferred_date}\n"
        f"🕐 Time: {preferred_time}\n"
        f"📋 Purpose: {purpose}\n\n"
        f"🔗 Trello: {card_url}\n\n"
        f"Our consultant will contact you at {email} to confirm.\n"
        f"For any queries, feel free to ask. Good luck with your study abroad journey! 🎓"
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
# 🤖 AGENT
# ============================
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="""You are a warm and professional study abroad consultant at Visa For You.

## Conversation Flow:
1. Greet the student warmly and introduce yourself
2. Collect: full name, email, phone number, CGPA, last degree — ONE question at a time
3. Once collected → call save_client_info immediately
4. Ask about their target field of study and annual budget
5. Call suggest_countries with budget and field
6. Answer any questions about specific countries using get_country_info
7. When student wants appointment → collect preferred date and time → call book_appointment

## Country Suggestions by CGPA:
- CGPA 3.5+: UK, USA, Germany, Canada, Australia
- CGPA 3.0-3.5: Canada, Australia, Germany, UK, Malaysia
- CGPA 2.5-3.0: Canada, Australia, Malaysia, China
- CGPA below 2.5: Malaysia, China

## Rules:
- Always pass user_id to every tool call
- Ask ONE question at a time
- Be encouraging — every student has options!
- Use knowledge base for accurate visa/scholarship/cost info
- Always mention free consultation availability
- Sign off as Visa For You Consultant"""
)

# ============================
# 🚀 RUN WITH MEMORY
# ============================
def run_agent(message: str, user_id: str = "default", channel: str = "web") -> str:
    if user_id not in client_info:
        client_info[user_id] = {}
    client_info[user_id]["channel"] = channel

    if user_id not in conversation_history:
        conversation_history[user_id] = []

    conversation_history[user_id].append(HumanMessage(content=message))
    result = agent.invoke({"messages": conversation_history[user_id]})
    conversation_history[user_id] = result["messages"]

    last_message = result["messages"][-1]
    if isinstance(last_message.content, list):
        return " ".join(
            block.get("text", "") if isinstance(block, dict) else str(block)
            for block in last_message.content
        )
    return str(last_message.content)