# services/langchain_agent.py

import os
import requests
import resend
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from slack_sdk import WebClient
from db.database import create_task, get_or_create_client, save_message
from datetime import datetime

load_dotenv()

# ============================
# ✅ GEMINI
# ============================
llm = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview",
    google_api_key=os.getenv("GEMINI_API_KEY")
)

# ============================
# 💬 CONVERSATION MEMORY
# ============================
conversation_history = {}
client_info = {}

def store_slack_id(user_id: str, slack_user_id: str):
    if user_id not in client_info:
        client_info[user_id] = {}
    client_info[user_id]["slack_user_id"] = slack_user_id

# ============================
# 🔧 TRELLO
# ============================
TRELLO_TODO_LIST_ID = "69ce483fd98acbd8128e9d9c"

def create_trello_card(task_name: str, description: str = ""):
    url = "https://api.trello.com/1/cards"
    params = {
        "key": os.getenv("TRELLO_API_KEY"),
        "token": os.getenv("TRELLO_TOKEN"),
        "idList": TRELLO_TODO_LIST_ID,
        "name": task_name,
        "desc": description
    }
    print(f"🔧 Creating Trello card: {task_name}")
    response = requests.post(url, params=params)
    print(f"🔧 Trello response: {response.status_code}")
    card = response.json()
    return card.get("shortUrl", "")

# ============================
# 📧 EMAIL
# ============================
def send_email_notification(task_name: str, requirements: str, card_url: str, client: dict):
    resend.api_key = os.getenv("RESEND_API_KEY")
    now = datetime.now().strftime("%B %d, %Y at %I:%M %p")

    req_lines = requirements.strip().split("\n")
    req_rows = "".join(
        f'<tr><td style="padding:8px 12px; border-bottom:1px solid #f0f0f0; color:#444; font-size:14px; line-height:1.6">{line}</td></tr>'
        for line in req_lines if line.strip()
    )

    html = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"></head>
    <body style="margin:0; padding:0; background:#f4f4f0; font-family: 'Helvetica Neue', Arial, sans-serif;">
      <table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f4f0; padding: 40px 0;">
        <tr><td align="center">
          <table width="620" cellpadding="0" cellspacing="0" style="background:#ffffff; border-radius:12px; overflow:hidden; border:1px solid #e8e8e6;">
            <tr>
              <td style="background:#1a1a1a; padding:32px 40px;">
                <p style="margin:0; font-size:11px; color:#888; letter-spacing:2px; text-transform:uppercase">DS Technologies</p>
                <h1 style="margin:8px 0 0; font-size:22px; font-weight:500; color:#ffffff; letter-spacing:-0.3px;">New Client Task</h1>
                <p style="margin:6px 0 0; font-size:13px; color:#888;">{now}</p>
              </td>
            </tr>
            <tr>
              <td style="background:#f0fdf4; padding:14px 40px; border-bottom:1px solid #bbf7d0;">
                <p style="margin:0; font-size:13px; color:#15803d; font-weight:500;">✅ Task successfully created and added to Trello</p>
              </td>
            </tr>
            <tr>
              <td style="padding:32px 40px;">
                <p style="margin:0 0 12px; font-size:11px; color:#999; letter-spacing:1.5px; text-transform:uppercase; font-weight:500;">Client Information</p>
                <table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e8e8e6; border-radius:8px; overflow:hidden; margin-bottom:28px;">
                  <tr style="background:#f9f9f8;">
                    <td style="padding:10px 16px; font-size:12px; color:#999; width:120px; border-bottom:1px solid #f0f0f0;">Full Name</td>
                    <td style="padding:10px 16px; font-size:14px; color:#1a1a1a; font-weight:500; border-bottom:1px solid #f0f0f0;">{client.get('name', 'Not provided')}</td>
                  </tr>
                  <tr>
                    <td style="padding:10px 16px; font-size:12px; color:#999; border-bottom:1px solid #f0f0f0;">Email</td>
                    <td style="padding:10px 16px; font-size:14px; color:#1a1a1a; border-bottom:1px solid #f0f0f0;"><a href="mailto:{client.get('email','')}" style="color:#3b5bdb; text-decoration:none;">{client.get('email', 'Not provided')}</a></td>
                  </tr>
                  <tr style="background:#f9f9f8;">
                    <td style="padding:10px 16px; font-size:12px; color:#999; border-bottom:1px solid #f0f0f0;">Phone</td>
                    <td style="padding:10px 16px; font-size:14px; color:#1a1a1a; border-bottom:1px solid #f0f0f0;"><a href="tel:{client.get('phone','')}" style="color:#3b5bdb; text-decoration:none;">{client.get('phone', 'Not provided')}</a></td>
                  </tr>
                  <tr>
                    <td style="padding:10px 16px; font-size:12px; color:#999;">Channel</td>
                    <td style="padding:10px 16px; font-size:14px; color:#1a1a1a; text-transform:capitalize;">{client.get('channel', 'Unknown')}</td>
                  </tr>
                </table>
                <p style="margin:0 0 12px; font-size:11px; color:#999; letter-spacing:1.5px; text-transform:uppercase; font-weight:500;">Project Details</p>
                <table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e8e8e6; border-radius:8px; overflow:hidden; margin-bottom:28px;">
                  <tr style="background:#f9f9f8;">
                    <td style="padding:10px 16px; font-size:12px; color:#999; width:120px; border-bottom:1px solid #f0f0f0;">Project Name</td>
                    <td style="padding:10px 16px; font-size:14px; color:#1a1a1a; font-weight:500; border-bottom:1px solid #f0f0f0;">{task_name}</td>
                  </tr>
                  <tr>
                    <td style="padding:10px 16px; font-size:12px; color:#999;">Trello Card</td>
                    <td style="padding:10px 16px; font-size:14px;"><a href="{card_url}" style="color:#3b5bdb; text-decoration:none; font-weight:500;">View on Trello →</a></td>
                  </tr>
                </table>
                <p style="margin:0 0 12px; font-size:11px; color:#999; letter-spacing:1.5px; text-transform:uppercase; font-weight:500;">Requirements Gathered</p>
                <table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e8e8e6; border-radius:8px; overflow:hidden; margin-bottom:28px;">
                  {req_rows}
                </table>
                <table cellpadding="0" cellspacing="0">
                  <tr>
                    <td style="border-radius:8px; background:#1a1a1a;">
                      <a href="{card_url}" style="display:inline-block; padding:12px 28px; font-size:14px; font-weight:500; color:#ffffff; text-decoration:none;">Open Trello Card →</a>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
            <tr>
              <td style="padding:24px 40px; border-top:1px solid #f0f0f0; background:#f9f9f8;">
                <p style="margin:0; font-size:12px; color:#bbb; line-height:1.6;">
                  This email was automatically generated by the DS Technologies AI Agent.<br/>
                  For queries, reply to this email or contact us directly.
                </p>
              </td>
            </tr>
          </table>
        </td></tr>
      </table>
    </body>
    </html>
    """

    try:
        resend.Emails.send({
            "from": "DS Technologies AI Agent <onboarding@resend.dev>",
            "to": os.getenv("NOTIFY_EMAIL"),
            "subject": f"🆕 New Project: {task_name} — {client.get('name', 'Unknown Client')}",
            "html": html
        })
        print("✅ Email sent successfully")
    except Exception as e:
        print(f"❌ Email error: {e}")

# ============================
# 🔔 SLACK TEAM NOTIFICATION
# ============================
def notify_slack_team(task_name: str, requirements: str, card_url: str, client: dict):
    slack_client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
    channel = os.getenv("SLACK_TEAM_CHANNEL", "#general")
    try:
        slack_client.chat_postMessage(
            channel=channel,
            text=(
                f"🆕 *New Client Project Received!*\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 *Client:* {client.get('name', 'Unknown')}\n"
                f"📧 *Email:* {client.get('email', 'N/A')}\n"
                f"📞 *Phone:* {client.get('phone', 'N/A')}\n"
                f"📡 *Channel:* {client.get('channel', 'N/A')}\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"📋 *Project:* {task_name}\n"
                f"📝 *Requirements:*\n{requirements[:500]}\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"🔗 *Trello:* {card_url}"
            )
        )
        print("✅ Slack team notified")
    except Exception as e:
        print(f"❌ Slack notify error: {e}")

# ============================
# 🛠️ TOOLS
# ============================

@tool
def save_client_info(name: str, email: str, phone: str, user_id: str) -> str:
    """
    Use this as soon as the client provides their name, email and phone number.
    user_id: pass the current user_id from the conversation
    """
    client_info[user_id] = {
        **client_info.get(user_id, {}),
        "name": name,
        "email": email,
        "phone": phone,
    }
    print(f"✅ Client info saved for {user_id}: {name}, {email}, {phone}")
    return f"Thank you {name}! Nice to meet you. Now, what project can I help you with today?"

@tool
def finalize_and_create_task(task_name: str, requirements: str, user_id: str) -> str:
    """
    Use this ONLY when the client has confirmed all requirements are complete.
    task_name: short clear title
    requirements: full requirements from conversation
    user_id: pass the current user_id
    """
    info           = client_info.get(user_id, {})
    name           = info.get("name", "Unknown")
    email          = info.get("email", "")
    phone          = info.get("phone", "")
    channel        = info.get("channel", "web")
    slack_user_id  = info.get("slack_user_id", "")

    # 1. Save client to DB
    client_id = get_or_create_client(
        name=name,
        channel=channel,
        phone=phone,
        email=email,
        slack_id=slack_user_id
    )
    print(f"✅ Client saved/found in DB: id={client_id}")

    # 2. Create Trello card
    card_url = create_trello_card(
        task_name=task_name,
        description=(
            f"👤 Client: {name}\n"
            f"📧 Email: {email}\n"
            f"📞 Phone: {phone}\n"
            f"📡 Channel: {channel}\n\n"
            f"📋 Requirements:\n{requirements}"
        )
    )

    # 3. Save task to DB
    create_task(
        description=f"{task_name}: {requirements}",
        trello_url=card_url,
        client_id=client_id
    )

    # 4. Send email
    client_dict = {"name": name, "email": email, "phone": phone, "channel": channel}
    send_email_notification(task_name, requirements, card_url, client_dict)

    # 5. Notify Slack
    notify_slack_team(task_name, requirements, card_url, client_dict)

    return (
        f"✅ Thank you {name}! Your project has been successfully submitted.\n\n"
        f"📋 *Project:* {task_name}\n"
        f"🔗 *Track your task:* {card_url}\n\n"
        f"📧 Our team will reach out to you at *{email}* shortly.\n"
        f"📞 We may also contact you at *{phone}* if needed.\n\n"
        f"For any queries, feel free to contact *DS Technologies Agent* anytime.\n"
        f"We look forward to working with you! 🚀"
    )

@tool
def get_services_info(query: str) -> str:
    """Use this when client asks about services, pricing, or what the company offers."""
    return """Here's what DS Technologies offers:

🌐 *Custom Web Development* — Modern, fast, and responsive websites
📱 *Mobile App Development* — iOS, Android & cross-platform apps
🤖 *AI & Automation Solutions* — Chatbots, agents, and workflow automation
🎨 *UI/UX Design* — Beautiful, user-centered design experiences
☁️ *Cloud & DevOps Services* — Scalable infrastructure and deployment
📈 *Digital Marketing* — SEO, social media, and growth strategies

💬 For pricing, we prepare custom quotes based on your project needs.
📞 Contact DS Technologies Agent for more details — we're happy to help!"""

tools = [save_client_info, finalize_and_create_task, get_services_info]

# ============================
# 🤖 AGENT
# ============================
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="""You are a professional AI assistant for DS Technologies, a software company.

## Conversation Flow:
1. Greet the client warmly and introduce yourself as DS Technologies AI Assistant
2. IMMEDIATELY ask for their full name, email address, and phone number
3. Once they provide all three → call save_client_info tool immediately
4. Ask what project or service they need
5. Ask ONE follow-up question at a time to gather complete requirements:
   - Websites: purpose, pages needed, design style, features, deadline, budget
   - Apps: platform (iOS/Android/both), core features, target audience, deadline, budget
   - AI/Automation: problem to solve, current workflow, integrations, deadline, budget
   - Always ask about timeline and budget range
6. Keep gathering requirements until client says 'done', 'that's all', 'create the task', 'finalize', or 'yes'
7. Summarize ALL gathered requirements clearly and ask client to confirm
8. Once client confirms → call finalize_and_create_task with complete details and user_id

## Rules:
- Always pass the exact user_id string when calling any tool
- Ask only ONE question at a time
- Be warm, professional, and concise
- NEVER create a task without explicit client confirmation
- If client asks about services → use get_services_info tool
- Always sign off as DS Technologies AI Assistant"""
)

# ============================
# 🚀 RUN AGENT WITH MEMORY
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