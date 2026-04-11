# services/visa_agent.py

import os
import resend
import requests
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from db.database import (
    save_chat_message, get_chat_history,
    create_appointment, get_user_by_email
)
from services.rag_engine import get_relevant_context
from datetime import datetime

load_dotenv()

# ✅ FIXED GEMINI INITIALIZATION
llm = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview",
    google_api_key=os.getenv("GEMINI_API_KEY")
)

TRELLO_TODO_LIST_ID = "69ce483fd98acbd8128e9d9c"

def create_trello_appointment(title: str, description: str) -> str:
    url = "https://api.trello.com/1/cards"
    params = {
        "key": os.getenv("TRELLO_API_KEY"),
        "token": os.getenv("TRELLO_TOKEN"),
        "idList": TRELLO_TODO_LIST_ID,
        "name": title,
        "desc": description
    }
    response = requests.post(url, params=params)
    return response.json().get("shortUrl", "")

def send_appointment_email(appointment: dict):
    resend.api_key = os.getenv("RESEND_API_KEY")
    now = datetime.now().strftime("%B %d, %Y at %I:%M %p")

    try:
        resend.Emails.send({
            "from": "Visa For You <onboarding@resend.dev>",
            "to": os.getenv("NOTIFY_EMAIL"),
            "subject": f"📅 New Appointment: {appointment['client_name']}",
            "html": f"<p>New appointment from {appointment['client_name']} at {now}</p>"
        })
        print("✅ Appointment email sent")
    except Exception as e:
        print(f"❌ Email error: {e}")


def run_visa_agent(message: str, user_id: int, user_data: dict) -> str:

    history = get_chat_history(user_id, limit=60)
    context = get_relevant_context(message)

    system_prompt = f"""
You are a friendly and professional study abroad consultant at Visa For You.

KNOWLEDGE BASE:
{context}

Student:
- Name: {user_data.get('name')}
- Email: {user_data.get('email')}
- CGPA: {user_data.get('cgpa')}
- Degree: {user_data.get('degree')}
- Phone: {user_data.get('phone')}

If user wants appointment respond:
BOOK_APPOINTMENT|date|time|purpose
"""

    messages = [SystemMessage(content=system_prompt)]

    for msg in history[-20:]:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        else:
            messages.append(AIMessage(content=msg["content"]))

    messages.append(HumanMessage(content=message))

    # ✅ GEMINI CALL (FIXED)
    response = llm.invoke(messages)
    reply = response.content

    # -----------------------------
    # APPOINTMENT HANDLING
    # -----------------------------
    if "BOOK_APPOINTMENT|" in reply:
        try:
            parts = reply.split("BOOK_APPOINTMENT|")[1].split("|")
            date = parts[0]
            time = parts[1]
            purpose = parts[2].split("\n")[0]

            trello_desc = f"""
Student: {user_data.get('name')}
Email: {user_data.get('email')}
Phone: {user_data.get('phone')}
CGPA: {user_data.get('cgpa')}
Degree: {user_data.get('degree')}
Date: {date}
Time: {time}
Purpose: {purpose}
"""

            card_url = create_trello_appointment(
                f"Appointment: {user_data.get('name')} - {date}",
                trello_desc
            )

            create_appointment(
                client_name=user_data.get('name'),
                client_email=user_data.get('email'),
                client_phone=user_data.get('phone'),
                preferred_date=date,
                preferred_time=time,
                purpose=purpose,
                trello_url=card_url,
                user_id=user_id
            )

            reply = f"""
✅ Appointment Booked!

📅 Date: {date}
🕐 Time: {time}
📋 Purpose: {purpose}

🔗 Trello: {card_url}
"""
        except Exception as e:
            print("❌ Appointment error:", e)

    save_chat_message(user_id, "user", message)
    save_chat_message(user_id, "ai", reply)

    return reply