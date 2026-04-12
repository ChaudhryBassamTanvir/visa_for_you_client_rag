# services/visa_agent.py

import os
import resend
import requests
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from db.database import (
    save_chat_message, get_chat_history,
    create_appointment, get_or_create_client
)
from services.rag_engine import get_relevant_context
from datetime import datetime

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview",
    google_api_key=os.getenv("GEMINI_API_KEY")
)

TRELLO_TODO_LIST_ID = "69ce483fd98acbd8128e9d9c"

def create_trello_appointment(title: str, description: str) -> str:
    url    = "https://api.trello.com/1/cards"
    params = {
        "key":    os.getenv("TRELLO_API_KEY"),
        "token":  os.getenv("TRELLO_TOKEN"),
        "idList": TRELLO_TODO_LIST_ID,
        "name":   title,
        "desc":   description
    }
    response = requests.post(url, params=params)
    if response.status_code == 200:
        return response.json().get("shortUrl", "")
    print(f"❌ Trello error: {response.status_code} {response.text}")
    return ""

def send_appointment_email(appointment: dict):
    resend.api_key = os.getenv("RESEND_API_KEY")
    now = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    try:
        resend.Emails.send({
            "from": "Visa For You <onboarding@resend.dev>",
            "to":   os.getenv("NOTIFY_EMAIL"),
            "subject": f"📅 New Appointment: {appointment['client_name']}",
            "html": f"""
            <body style="font-family:Arial,sans-serif;background:#f4f4f0;padding:40px 0;">
              <table width="600" style="margin:auto;background:#fff;border-radius:12px;overflow:hidden;border:1px solid #e8e8e6;">
                <tr><td style="background:#1a1a1a;padding:28px 36px;">
                  <h1 style="color:#fff;margin:0;font-size:20px;font-weight:500;">New Appointment Request</h1>
                  <p style="color:#888;margin:4px 0 0;font-size:13px;">{now}</p>
                </td></tr>
                <tr><td style="padding:28px 36px;">
                  <table width="100%" style="border:1px solid #e8e8e6;border-radius:8px;overflow:hidden;">
                    <tr style="background:#f9f9f8;"><td style="padding:10px 16px;font-size:12px;color:#999;width:130px;">Client Name</td><td style="padding:10px 16px;font-size:14px;font-weight:500;">{appointment['client_name']}</td></tr>
                    <tr><td style="padding:10px 16px;font-size:12px;color:#999;border-top:1px solid #f0f0f0;">Email</td><td style="padding:10px 16px;font-size:14px;border-top:1px solid #f0f0f0;">{appointment['client_email']}</td></tr>
                    <tr style="background:#f9f9f8;"><td style="padding:10px 16px;font-size:12px;color:#999;border-top:1px solid #f0f0f0;">Phone</td><td style="padding:10px 16px;font-size:14px;border-top:1px solid #f0f0f0;">{appointment['client_phone']}</td></tr>
                    <tr><td style="padding:10px 16px;font-size:12px;color:#999;border-top:1px solid #f0f0f0;">Date</td><td style="padding:10px 16px;font-size:14px;border-top:1px solid #f0f0f0;">{appointment['preferred_date']}</td></tr>
                    <tr style="background:#f9f9f8;"><td style="padding:10px 16px;font-size:12px;color:#999;border-top:1px solid #f0f0f0;">Time</td><td style="padding:10px 16px;font-size:14px;border-top:1px solid #f0f0f0;">{appointment['preferred_time']}</td></tr>
                    <tr><td style="padding:10px 16px;font-size:12px;color:#999;border-top:1px solid #f0f0f0;">Purpose</td><td style="padding:10px 16px;font-size:14px;border-top:1px solid #f0f0f0;">{appointment['purpose']}</td></tr>
                    <tr style="background:#f9f9f8;"><td style="padding:10px 16px;font-size:12px;color:#999;border-top:1px solid #f0f0f0;">CGPA</td><td style="padding:10px 16px;font-size:14px;border-top:1px solid #f0f0f0;">{appointment.get('cgpa','N/A')}</td></tr>
                    <tr><td style="padding:10px 16px;font-size:12px;color:#999;border-top:1px solid #f0f0f0;">Degree</td><td style="padding:10px 16px;font-size:14px;border-top:1px solid #f0f0f0;">{appointment.get('degree','N/A')}</td></tr>
                  </table>
                  <br/>
                  <a href="{appointment.get('trello_url','#')}" style="display:inline-block;padding:11px 24px;background:#1a1a1a;color:#fff;border-radius:8px;text-decoration:none;font-size:13px;font-weight:500;">View on Trello →</a>
                </td></tr>
                <tr><td style="padding:20px 36px;border-top:1px solid #f0f0f0;background:#f9f9f8;">
                  <p style="margin:0;font-size:12px;color:#bbb;">Visa For You Consultancy — Automated Appointment System</p>
                </td></tr>
              </table>
            </body>
            """
        })
        print("✅ Appointment email sent")
    except Exception as e:
        print(f"❌ Email error: {e}")

# Per-session memory for Slack/WA users (web users use DB)
session_data = {}  # { user_id: { name, email, phone, cgpa, degree } }

def run_visa_agent(message: str, user_id: int, user_data: dict) -> str:
    str_user_id = str(user_id)

    # Merge DB user_data with session collected data
    if str_user_id not in session_data:
        session_data[str_user_id] = {}
    session = session_data[str_user_id]

    # Update session with any known user_data
    for key in ["name", "email", "phone", "cgpa", "degree"]:
        if user_data.get(key) and not session.get(key):
            session[key] = user_data[key]

    name   = session.get("name")   or user_data.get("name", "")
    email  = session.get("email")  or user_data.get("email", "")
    phone  = session.get("phone")  or user_data.get("phone", "")
    cgpa   = session.get("cgpa")   or user_data.get("cgpa", "")
    degree = session.get("degree") or user_data.get("degree", "")

    # Get context from knowledge base
    context = get_relevant_context(message)

    # Get last 20 messages for context
    history = get_chat_history(user_id, limit=60)

    system_prompt = f"""You are a friendly study abroad consultant at Visa For You.

Student Profile:
- Name: {name or 'Not provided'}
- Email: {email or 'Not provided'}  
- Phone: {phone or 'Not provided'}
- CGPA: {cgpa or 'Not provided'}
- Degree: {degree or 'Not provided'}

KNOWLEDGE BASE:
{context}

YOUR JOB:
1. If name/email/phone/CGPA/degree missing → ask ONE at a time
2. Once profile complete → suggest countries based on CGPA:
   - CGPA < 2.5: Malaysia, China
   - CGPA 2.5-3.0: Canada, Australia, Malaysia  
   - CGPA > 3.0: UK, USA, Germany, Canada, Australia
3. Answer questions using knowledge base
4. When student wants appointment → ask date and time → then output EXACTLY:
   BOOK_APPOINTMENT|{{date}}|{{time}}|{{purpose}}

RULES:
- Keep responses SHORT (max 3-4 lines)
- Ask ONE question at a time
- Never show BOOK_APPOINTMENT text to student
- Be warm and encouraging
- Always save info student provides by updating your understanding

When student gives their name, save it. When they give CGPA save it. Build profile gradually."""

    messages = [SystemMessage(content=system_prompt)]
    for msg in history[-20:]:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        else:
            messages.append(AIMessage(content=msg["content"]))
    messages.append(HumanMessage(content=message))

    response = llm.invoke(messages)
    reply    = response.content

    # Extract info from message to update session
    _extract_and_save_session(str_user_id, message, reply)

    # Handle appointment booking
    if "BOOK_APPOINTMENT|" in reply:
        try:
            booking_part = reply.split("BOOK_APPOINTMENT|")[1]
            parts        = booking_part.split("|")
            date         = parts[0].strip()
            time         = parts[1].strip()
            purpose      = parts[2].strip().split("\n")[0]

            # Use session data for client info
            client_name  = session.get("name")  or name  or "Unknown"
            client_email = session.get("email") or email or ""
            client_phone = session.get("phone") or phone or ""
            client_cgpa  = session.get("cgpa")  or cgpa  or ""
            client_degree= session.get("degree")or degree or ""

            # Create Trello card
            trello_desc = (
                f"👤 Student: {client_name}\n"
                f"📧 Email: {client_email}\n"
                f"📞 Phone: {client_phone}\n"
                f"🎓 CGPA: {client_cgpa}\n"
                f"📚 Degree: {client_degree}\n"
                f"📅 Date: {date}\n"
                f"🕐 Time: {time}\n"
                f"📋 Purpose: {purpose}"
            )
            card_url = create_trello_appointment(
                f"📅 {client_name} — {date} {time}",
                trello_desc
            )

            # Save appointment to DB
           # ✅ Correct
            create_appointment(
             client_name=client_name,
             client_email=client_email,
             client_phone=client_phone,
             preferred_date=date,
             preferred_time=time,
             purpose=purpose,
             trello_url=card_url,
             user_id=user_id          # ✅ correct parameter name
                            )
            # Send email notification
            send_appointment_email({
                "client_name":    client_name,
                "client_email":   client_email,
                "client_phone":   client_phone,
                "preferred_date": date,
                "preferred_time": time,
                "purpose":        purpose,
                "trello_url":     card_url,
                "cgpa":           client_cgpa,
                "degree":         client_degree,
            })

            reply = (
                f"✅ Appointment booked!\n\n"
                f"📅 {date} at {time}\n"
                f"📋 {purpose}\n\n"
                f"Our consultant will confirm via email. See you soon! 🎓"
            )

        except Exception as e:
            print(f"❌ Appointment booking error: {e}")
            reply = "I'd like to book your appointment. Could you please provide your preferred date and time?"

    # Save to DB
    save_chat_message(user_id, "user", message)
    save_chat_message(user_id, "ai",   reply)

    return reply

def _extract_and_save_session(user_id: str, message: str, reply: str):
    """Try to extract profile info from conversation"""
    if user_id not in session_data:
        session_data[user_id] = {}
    # Simple keyword extraction — agent handles the actual extraction via prompting
    msg_lower = message.lower()
    if "cgpa" in msg_lower or any(c.isdigit() and "." in message for c in message):
        # Try to find CGPA pattern like 3.5, 2.8 etc
        import re
        cgpa_match = re.search(r'\b[0-4]\.\d{1,2}\b', message)
        if cgpa_match and not session_data[user_id].get("cgpa"):
            session_data[user_id]["cgpa"] = cgpa_match.group()