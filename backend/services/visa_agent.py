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
    model="gemini-1.5-flash",
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
        print("✅ Trello appointment card created")
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
                    <tr style="background:#f9f9f8;"><td style="padding:10px 16px;font-size:12px;color:#999;width:130px;">Name</td><td style="padding:10px 16px;font-size:14px;font-weight:500;">{appointment['client_name']}</td></tr>
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
                  <p style="margin:0;font-size:12px;color:#bbb;">Visa For You — Automated Appointment System</p>
                </td></tr>
              </table>
            </body>
            """
        })
        print("✅ Appointment email sent")
    except Exception as e:
        print(f"❌ Email error: {e}")

def run_visa_agent(message: str, user_id: int, user_data: dict) -> str:
    # Use user_id as string key for chat history
    history_key = f"visa_{user_id}"

    # Get last 60 messages from DB
    history = get_chat_history(user_id, limit=60)

    # Get RAG context
    context = get_relevant_context(message)

    name   = user_data.get('name', 'Student')
    email  = user_data.get('email', '')
    cgpa   = user_data.get('cgpa', '')
    degree = user_data.get('degree', '')
    phone  = user_data.get('phone', '')

    system_prompt = f"""You are a study abroad consultant at Visa For You.

Student: {name} | Email: {email} | CGPA: {cgpa} | Degree: {degree} | Phone: {phone}

KNOWLEDGE BASE:
{context}

RULES:
- Be SHORT and DIRECT — max 3-4 lines per response
- Ask ONE question at a time
- If CGPA < 2.5: suggest Malaysia, China
- If CGPA 2.5-3.0: suggest Canada, Australia, Malaysia  
- If CGPA > 3.0: suggest UK, USA, Germany, Canada, Australia
- Mention scholarships when relevant
- For appointments: collect date, time, purpose then respond EXACTLY:
  BOOK_APPOINTMENT|date|time|purpose

Never write long paragraphs. Be concise."""

    messages = [SystemMessage(content=system_prompt)]
    for msg in history[-20:]:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        else:
            messages.append(AIMessage(content=msg["content"]))
    messages.append(HumanMessage(content=message))

    response = llm.invoke(messages)
    reply    = response.content

    # Handle appointment booking
    if "BOOK_APPOINTMENT|" in reply:
        try:
            parts   = reply.split("BOOK_APPOINTMENT|")[1].split("|")
            date    = parts[0].strip()
            time    = parts[1].strip()
            purpose = parts[2].strip().split("\n")[0]

            trello_desc = (
                f"👤 Student: {name}\n"
                f"📧 Email: {email}\n"
                f"📞 Phone: {phone}\n"
                f"🎓 CGPA: {cgpa}\n"
                f"📚 Degree: {degree}\n"
                f"📅 Date: {date}\n"
                f"🕐 Time: {time}\n"
                f"📋 Purpose: {purpose}"
            )

            card_url = create_trello_appointment(
                f"📅 {name} — {date} {time}",
                trello_desc
            )

            # Save appointment to DB
            create_appointment(
                client_name=name,
                client_email=email,
                client_phone=phone,
                preferred_date=date,
                preferred_time=time,
                purpose=purpose,
                trello_url=card_url,
                user_id=user_id
            )

            # Send email
            send_appointment_email({
                "client_name":    name,
                "client_email":   email,
                "client_phone":   phone,
                "preferred_date": date,
                "preferred_time": time,
                "purpose":        purpose,
                "cgpa":           cgpa,
                "degree":         degree,
                "trello_url":     card_url
            })

            reply = (
                f"✅ Appointment booked!\n"
                f"📅 {date} at {time}\n"
                f"📋 {purpose}\n\n"
                f"Our consultant will confirm via email. See you soon! 🎓"
            )
        except Exception as e:
            print(f"❌ Appointment error: {e}")
            reply = "✅ Appointment request received! Our team will contact you to confirm. 🎓"

    # Save to DB
    save_chat_message(user_id, "user", message)
    save_chat_message(user_id, "ai",   reply)

    return reply