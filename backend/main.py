# main.py

import os
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from services.whatsapp_bot import send_whatsapp_message
from services.auth import register_user, login_user, decode_token
from services.visa_agent import run_visa_agent
from services.langchain_agent import run_agent, is_duplicate_message
from services.rag_engine import load_knowledge_base
from services.trello_service import move_trello_card

from db.database import (
    init_db, get_all_tasks, get_all_clients, get_dashboard_stats,
    update_task_status, update_task_status_by_trello_url,
    get_task_trello_url, get_all_appointments, get_user_by_email,
    update_user_profile, get_chat_history, get_or_create_client,
    delete_client, update_appointment_status, add_client_manual,
    get_all_users, delete_appointment, create_appointment,
    Appointment, SessionLocal
)
from dotenv import load_dotenv
import resend

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()
init_db()
load_knowledge_base()

# ============================
# 🔐 AUTH HELPER
# ============================
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token   = credentials.credentials
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload

# ============================
# 🔐 AUTH ENDPOINTS
# ============================
@app.post("/auth/signup")
async def signup(data: dict):
    name     = data.get("name", "").strip()
    email    = data.get("email", "").strip()
    password = data.get("password", "").strip()
    if not all([name, email, password]):
        raise HTTPException(status_code=400, detail="Name, email and password required")
    token, error = register_user(name, email, password)
    if error:
        raise HTTPException(status_code=400, detail=error)
    user = get_user_by_email(email)
    return {
        "token":    token,
        "name":     user.name,
        "email":    user.email,
        "is_admin": user.is_admin,
        "cgpa":     user.cgpa,
        "degree":   user.degree,
        "phone":    user.phone,
    }

@app.post("/auth/login")
async def login(data: dict):
    email    = data.get("email", "").strip()
    password = data.get("password", "").strip()
    token, user, error = login_user(email, password)
    if error:
        raise HTTPException(status_code=401, detail=error)
    return {
        "token":    token,
        "name":     user.name,
        "email":    user.email,
        "is_admin": user.is_admin,
        "cgpa":     user.cgpa,
        "degree":   user.degree,
        "phone":    user.phone,
    }

@app.post("/auth/admin/create")
async def create_admin(data: dict):
    secret = data.get("secret")
    if secret != os.getenv("ADMIN_SECRET", "admin-visa-2024"):
        raise HTTPException(status_code=403, detail="Invalid secret")
    token, error = register_user(
        data.get("name"), data.get("email"),
        data.get("password"), is_admin=True
    )
    if error:
        raise HTTPException(status_code=400, detail=error)
    return {"message": "Admin created", "token": token}

# ============================
# 👤 USER PROFILE
# ============================
@app.put("/user/profile")
async def update_profile(data: dict, user=Depends(get_current_user)):
    update_user_profile(
        user_id=user["user_id"],
        cgpa=data.get("cgpa", ""),
        degree=data.get("degree", ""),
        phone=data.get("phone", "")
    )
    return {"success": True}

# ============================
# 🎓 VISA AGENT CHAT
# ============================
@app.post("/visa/chat")
async def visa_chat(data: dict, user=Depends(get_current_user)):
    message = data.get("message", "").strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message required")
    db_user   = get_user_by_email(user["email"])
    user_data = {
        "name":   db_user.name,
        "email":  db_user.email,
        "cgpa":   db_user.cgpa or "",
        "degree": db_user.degree or "",
        "phone":  db_user.phone or "",
    }
    response = run_visa_agent(message, user["user_id"], user_data)
    return {"response": response}

@app.get("/visa/history")
async def visa_history(user=Depends(get_current_user)):
    return get_chat_history(user["user_id"], limit=60)

# ============================
# 📊 ADMIN ENDPOINTS
# ============================
@app.get("/tasks")
async def get_tasks():
    return get_all_tasks()

@app.get("/clients")
async def get_clients():
    return get_all_clients()

@app.get("/stats")
async def get_stats():
    return get_dashboard_stats()

@app.get("/users")
async def get_users():
    return get_all_users()

@app.patch("/tasks/{task_id}")
async def update_task(task_id: int, data: dict):
    new_status = data.get("status", "pending")
    update_task_status(task_id, new_status)
    trello_url = get_task_trello_url(task_id)
    if trello_url:
        move_trello_card(trello_url, new_status)
    return {"success": True}

@app.post("/clients")
async def add_client(data: dict):
    client_id = add_client_manual(
        name=data.get("name", ""),
        email=data.get("email", ""),
        phone=data.get("phone", ""),
        company=data.get("company", ""),
        channel=data.get("channel", "web"),
        university=data.get("university", ""),
        target_country=data.get("target_country", ""),
        cgpa=data.get("cgpa", ""),
        degree=data.get("degree", ""),
    )
    return {"id": client_id, "success": True}

@app.delete("/clients/{client_id}")
async def delete_client_endpoint(client_id: int):
    success = delete_client(client_id)
    if not success:
        raise HTTPException(status_code=400, detail="Could not delete client")
    return {"success": True}

# ============================
# 📅 APPOINTMENTS
# ============================
@app.get("/appointments")
async def get_appointments(user=Depends(get_current_user)):
    if not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin only")
    return get_all_appointments()

@app.patch("/appointments/{appt_id}")
async def update_appt(appt_id: int, data: dict, user=Depends(get_current_user)):
    if not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin only")
    new_status = data.get("status")
    trello_url = update_appointment_status(appt_id, new_status)
    if trello_url and new_status == "done":
        move_trello_card(trello_url, "done")
    return {"success": True}

@app.delete("/appointments/{appt_id}")
async def delete_appt(appt_id: int, user=Depends(get_current_user)):
    if not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin only")
    success = delete_appointment(appt_id)
    if not success:
        raise HTTPException(status_code=404, detail="Not found")
    return {"success": True}

# ──────────────────────────────────────────────────────────────────
# ✅  NEW: Send confirmation email to client from Appointments page
# ──────────────────────────────────────────────────────────────────
@app.post("/appointments/{appt_id}/send-email")
async def send_appt_email_to_client(appt_id: int, user=Depends(get_current_user)):
    """Admin clicks 'Send to client' → fires the confirmation email to the client."""
    if not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin only")

    db = SessionLocal()
    try:
        appt = db.query(Appointment).filter(Appointment.id == appt_id).first()
        if not appt:
            raise HTTPException(status_code=404, detail="Appointment not found")
        if not appt.client_email:
            raise HTTPException(status_code=400, detail="No email on record for this appointment")

        resend.api_key = os.getenv("RESEND_API_KEY")
        rows = "".join(
            f'<tr><td style="padding:8px 16px;font-size:12px;color:#999;width:160px;border-bottom:1px solid #f0f0f0">{k}</td>'
            f'<td style="padding:8px 16px;font-size:14px;color:#1a1a1a;border-bottom:1px solid #f0f0f0">{v}</td></tr>'
            for k, v in {
                "Date":    appt.preferred_date,
                "Time":    appt.preferred_time,
                "Purpose": appt.purpose,
            }.items() if v
        )
        html = f"""
        <body style="font-family:Arial,sans-serif;background:#f4f4f0;padding:40px 0;">
          <table width="600" style="margin:auto;background:#fff;border-radius:12px;overflow:hidden;border:1px solid #e8e8e6;">
            <tr><td style="background:#1a1a1a;padding:28px 36px;">
              <p style="margin:0;font-size:11px;color:#888;letter-spacing:2px;text-transform:uppercase">Visa For You</p>
              <h1 style="margin:8px 0 0;font-size:20px;font-weight:500;color:#fff;">Appointment Confirmed ✓</h1>
            </td></tr>
            <tr><td style="padding:28px 36px;">
              <p style="margin:0 0 6px;font-size:22px;font-weight:600;color:#111;">Hi {appt.client_name},</p>
              <p style="margin:0 0 24px;font-size:14px;color:#888;">Your consultation with Visa For You is confirmed:</p>
              <table width="100%" style="border:1px solid #e8e8e6;border-radius:8px;overflow:hidden;margin-bottom:24px;">{rows}</table>
              <p style="font-size:13px;color:#888;margin:0;">
                Our consultant will reach out before the appointment.
                Reply to this email if you need to reschedule.
              </p>
            </td></tr>
            <tr><td style="padding:20px 36px;border-top:1px solid #f0f0f0;background:#f9f9f8;">
              <p style="margin:0;font-size:12px;color:#bbb;">Visa For You · team@dstech.pk</p>
            </td></tr>
          </table>
        </body>
        """
        resend.Emails.send({
            "from":    "Visa For You <onboarding@resend.dev>",
            "to":      appt.client_email,
            "subject": "Your Appointment is Confirmed — Visa For You",
            "html":    html,
        })

        # Mark email_sent on the appointment (optional field — add to model if needed)
        if hasattr(appt, "email_sent"):
            appt.email_sent = True
            db.commit()

        print(f"✅ Confirmation email sent to {appt.client_email}")
        return {"success": True, "sent_to": appt.client_email}

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ send-email error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

# ──────────────────────────────────────────────────────────────────
# ✅  NEW: Promote appointment → Client record
# ──────────────────────────────────────────────────────────────────
@app.post("/appointments/{appt_id}/promote-to-client")
async def promote_to_client(appt_id: int, user=Depends(get_current_user)):
    """
    When admin clicks 'Add as Client' on a done appointment,
    this creates / updates the client record from the appointment data.
    """
    if not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin only")

    db = SessionLocal()
    try:
        appt = db.query(Appointment).filter(Appointment.id == appt_id).first()
        if not appt:
            raise HTTPException(status_code=404, detail="Appointment not found")

        client_id = get_or_create_client(
            name    = appt.client_name  or "Unknown",
            channel = "web",
            phone   = appt.client_phone or "",
            email   = appt.client_email or "",
        )

        # Mark as promoted so the UI can reflect it
        if hasattr(appt, "promoted_to_client"):
            appt.promoted_to_client = True
            db.commit()

        return {"success": True, "client_id": client_id}
    finally:
        db.close()

# ============================
# 📱 WHATSAPP WEBHOOK
# ============================
@app.get("/whatsapp/webhook")
async def verify_webhook(request: Request):
    params    = dict(request.query_params)
    mode      = params.get("hub.mode")
    token     = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")
    if mode == "subscribe" and token == os.getenv("WHATSAPP_VERIFY_TOKEN"):
        return Response(content=challenge, media_type="text/plain")
    return Response(content="Forbidden", status_code=403)

@app.post("/whatsapp/webhook")
async def whatsapp_webhook(request: Request):
    data = await request.json()
    try:
        entry   = data["entry"][0]
        changes = entry["changes"][0]
        value   = changes["value"]
        if "messages" not in value:
            return {"status": "no message"}

        message_data = value["messages"][0]
        from_number  = message_data["from"]

        # ── Dedup using WhatsApp message ID ───────────────────
        wa_msg_id = message_data.get("id", "")
        if wa_msg_id and is_duplicate_message(wa_msg_id):
            print(f"⚠️  Duplicate WhatsApp message {wa_msg_id} — ignoring")
            return {"status": "duplicate"}

        if message_data.get("type") != "text":
            send_whatsapp_message(from_number, "Sorry, I can only process text messages.")
            return {"status": "non-text"}

        user_message = message_data["text"]["body"]
        print(f"📱 WhatsApp from {from_number}: {user_message}")

        client_id = get_or_create_client(
            name=f"WA {from_number}", channel="whatsapp", phone=from_number
        )
        user_data = {
            "name": f"WA {from_number}", "email": "", "cgpa": "", "degree": "", "phone": from_number,
        }
        response = run_visa_agent(user_message, user_id=int(client_id), user_data=user_data)
        if response:
            send_whatsapp_message(from_number, response)

    except Exception as e:
        print(f"❌ WhatsApp error: {e}")
    return {"status": "ok"}

# ============================
# 🔲 TRELLO WEBHOOK
# ============================
@app.head("/trello/webhook")
async def trello_webhook_head():
    return Response(status_code=200)

@app.get("/trello/webhook")
async def trello_webhook_verify():
    return {"status": "ok"}

@app.post("/trello/webhook")
async def trello_webhook(request: Request):
    try:
        data       = await request.json()
        action     = data.get("action", {})
        if action.get("type") != "updateCard":
            return {"status": "ignored"}
        card_data  = action.get("data", {})
        card       = card_data.get("card", {})
        list_after = card_data.get("listAfter", {})
        if not list_after:
            return {"status": "no list change"}
        card_url   = f"https://trello.com/c/{card.get('shortLink', '')}"
        list_name  = list_after.get("name", "").lower()
        status_map = {
            "to do": "pending", "doing": "in_progress",
            "in progress": "in_progress", "done": "done"
        }
        new_status = status_map.get(list_name)
        if new_status:
            update_task_status_by_trello_url(card_url, new_status)
    except Exception as e:
        print(f"❌ Trello webhook error: {e}")
    return {"status": "ok"}