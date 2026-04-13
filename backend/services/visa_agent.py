# services/visa_agent.py

import os
import re
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

TRELLO_TODO_LIST_ID = os.getenv("TRELLO_LIST_ID", "69ce483fd98acbd8128e9d9c")


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
    print(f"Trello error: {response.status_code} {response.text}")
    return ""


def send_appointment_email(appointment: dict):
    resend.api_key = os.getenv("RESEND_API_KEY")
    now = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    try:
        resend.Emails.send({
            "from": "Visa For You <onboarding@resend.dev>",
            "to":   os.getenv("NOTIFY_EMAIL"),
            "subject": f"New Appointment: {appointment['client_name']}",
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
                  <a href="{appointment.get('trello_url','#')}" style="display:inline-block;padding:11px 24px;background:#1a1a1a;color:#fff;border-radius:8px;text-decoration:none;font-size:13px;font-weight:500;">View on Trello</a>
                </td></tr>
                <tr><td style="padding:20px 36px;border-top:1px solid #f0f0f0;background:#f9f9f8;">
                  <p style="margin:0;font-size:12px;color:#bbb;">Visa For You Consultancy — Automated Appointment System</p>
                </td></tr>
              </table>
            </body>
            """
        })
        print("Appointment email sent")
    except Exception as e:
        print(f"Email error: {e}")


# Per-session memory for Slack/WA users
session_data = {}


def _extract_and_save_session(user_id: str, message: str):
    """
    Extract profile info from the user's raw message and persist it to
    session_data so we never ask for something they already provided.
    """
    if user_id not in session_data:
        session_data[user_id] = {}

    s = session_data[user_id]

    # --- CGPA ---
    cgpa_match = re.search(r'\b([0-4]\.\d{1,2})\b', message)
    if cgpa_match and not s.get("cgpa"):
        s["cgpa"] = cgpa_match.group(1)

    # --- Email ---
    email_match = re.search(r'[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}', message)
    if email_match and not s.get("email"):
        s["email"] = email_match.group(0)

    # --- Phone (international format or local) ---
    phone_match = re.search(r'(\+?\d[\d\s\-]{8,14}\d)', message)
    if phone_match and not s.get("phone"):
        candidate = re.sub(r'[\s\-]', '', phone_match.group(1))
        # Avoid matching CGPA-like numbers
        if len(candidate) >= 9:
            s["phone"] = candidate

    # --- Degree keywords ---
    degree_keywords = [
        "bs", "ms", "msc", "bsc", "mba", "phd", "bachelor", "master",
        "b.s", "m.s", "b.sc", "m.sc", "be", "beng", "meng"
    ]
    msg_lower = message.lower()
    if not s.get("degree"):
        for kw in degree_keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', msg_lower):
                # Try to grab degree + subject, e.g. "BS SE", "Masters in IT"
                deg_match = re.search(
                    r'\b(bs|ms|msc|bsc|mba|phd|bachelor|master|b\.s|m\.s|b\.sc|m\.sc|be|beng|meng)'
                    r'[\s\w]{0,30}',
                    msg_lower
                )
                if deg_match:
                    s["degree"] = deg_match.group(0).strip().title()
                break

    # --- Name: simple heuristic — first capitalised token pair not matching other fields ---
    if not s.get("name") or s["name"].startswith("WA "):
        # Look for "Name: Xyz" or two consecutive Title Case words
        name_match = re.search(r'(?:my name is|i am|i\'m|name[:\-]?\s*)([A-Z][a-z]+(?: [A-Z][a-z]+)+)', message)
        if not name_match:
            # Two consecutive title-case words not at start of sentence punctuation
            name_match = re.search(r'\b([A-Z][a-z]{1,15} [A-Z][a-z]{1,15})\b', message)
        if name_match:
            candidate = name_match.group(1)
            # Make sure it's not a university / country name
            skip = {"Aberdeen", "University", "Birmingham", "Malaysia", "Canada", "Australia"}
            parts = candidate.split()
            if not any(p in skip for p in parts):
                s["name"] = candidate


def run_visa_agent(message: str, user_id: int, user_data: dict) -> str:
    str_user_id = str(user_id)

    if str_user_id not in session_data:
        session_data[str_user_id] = {}

    session = session_data[str_user_id]

    # Seed session with known user_data (only if not already richer)
    for key in ["name", "email", "phone", "cgpa", "degree"]:
        val = user_data.get(key, "")
        if val and not session.get(key):
            session[key] = val

    # Extract info from THIS message before calling LLM
    _extract_and_save_session(str_user_id, message)

    name   = session.get("name")   or ""
    email  = session.get("email")  or ""
    phone  = session.get("phone")  or user_data.get("phone", "")
    cgpa   = session.get("cgpa")   or ""
    degree = session.get("degree") or ""

    context = get_relevant_context(message)
    history = get_chat_history(user_id, limit=60)

    # Build a profile summary so the LLM knows what we already have
    profile_status = []
    if name   and not name.startswith("WA "): profile_status.append(f"Name: {name}")
    if email:   profile_status.append(f"Email: {email}")
    if phone:   profile_status.append(f"Phone: {phone}")
    if cgpa:    profile_status.append(f"CGPA: {cgpa}")
    if degree:  profile_status.append(f"Degree: {degree}")
    known = "\n".join(profile_status) if profile_status else "Nothing collected yet"

    missing = []
    if not name or name.startswith("WA "):  missing.append("full name")
    if not email:   missing.append("email")
    if not phone or phone == user_data.get("phone",""):
        pass  # phone already known from WA number
    if not cgpa:    missing.append("CGPA")
    if not degree:  missing.append("last degree")

    system_prompt = f"""You are a friendly study abroad consultant at Visa For You.

ALREADY KNOWN PROFILE:
{known}

STILL MISSING: {", ".join(missing) if missing else "Nothing — profile complete!"}

KNOWLEDGE BASE:
{context}

YOUR JOB:
1. NEVER ask for information already in ALREADY KNOWN PROFILE above.
2. If STILL MISSING is not empty, ask for ONE missing field at a time.
3. Once profile is complete, suggest countries based on CGPA:
   - CGPA < 2.5: Malaysia, China
   - CGPA 2.5-3.0: Canada, Australia, Malaysia
   - CGPA >= 3.0: UK, USA, Germany, Canada, Australia
4. Answer questions using the knowledge base.
5. When student wants to book appointment, ask for date and time if not provided,
   then output EXACTLY on its own line (never show this to student):
   BOOK_APPOINTMENT|{{date}}|{{time}}|{{purpose}}

RULES:
- Keep responses SHORT (2-4 lines max).
- Ask ONE question at a time.
- Be warm and encouraging.
- If student gave ALL info in one message, proceed directly — do NOT re-ask anything."""

    messages = [SystemMessage(content=system_prompt)]
    for msg in history[-20:]:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        else:
            messages.append(AIMessage(content=msg["content"]))
    messages.append(HumanMessage(content=message))

    response = llm.invoke(messages)

    # Safely extract plain string from LangChain response
    reply = response.content
    if isinstance(reply, list):
        reply = " ".join(
            block.get("text", "") if isinstance(block, dict) else getattr(block, "text", str(block))
            for block in reply
            if (block.get("type") == "text" if isinstance(block, dict) else getattr(block, "type", "") == "text")
        )
    reply = str(reply).strip()

    # Handle appointment booking
    if "BOOK_APPOINTMENT|" in reply:
        try:
            booking_part = reply.split("BOOK_APPOINTMENT|")[1]
            parts        = booking_part.split("|")
            date         = parts[0].strip()
            time         = parts[1].strip()
            purpose      = parts[2].strip().split("\n")[0]

            client_name  = session.get("name")   or name   or "Unknown"
            client_email = session.get("email")  or email  or ""
            client_phone = session.get("phone")  or phone  or ""
            client_cgpa  = session.get("cgpa")   or cgpa   or ""
            client_degree= session.get("degree") or degree or ""

            trello_desc = (
                f"Student: {client_name}\n"
                f"Email: {client_email}\n"
                f"Phone: {client_phone}\n"
                f"CGPA: {client_cgpa}\n"
                f"Degree: {client_degree}\n"
                f"Date: {date}\n"
                f"Time: {time}\n"
                f"Purpose: {purpose}"
            )
            card_url = create_trello_appointment(
                f"{client_name} - {date} {time}",
                trello_desc
            )

            # FIX: WhatsApp clients are in the clients table, NOT users table.
            # Pass user_id=None to avoid FK violation on appointments.user_id -> users.id
            create_appointment(
                client_name=client_name,
                client_email=client_email,
                client_phone=client_phone,
                preferred_date=date,
                preferred_time=time,
                purpose=purpose,
                trello_url=card_url,
                user_id=None        # WA/Slack clients are not in users table
            )

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
                f"Appointment booked!\n\n"
                f"Date: {date} at {time}\n"
                f"Purpose: {purpose}\n\n"
                f"Our consultant will confirm via email. See you soon!"
            )

        except Exception as e:
            print(f"Appointment booking error: {e}")
            reply = "I'd like to book your appointment. Could you please confirm your preferred date and time?"

    save_chat_message(user_id, "user", message)
    save_chat_message(user_id, "ai",   reply)

    return str(reply).strip()