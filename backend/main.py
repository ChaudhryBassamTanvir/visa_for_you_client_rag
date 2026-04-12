# main.py

import os
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from services.langchain_agent import run_agent
from services.whatsapp_bot import send_whatsapp_message
from services.auth import register_user, login_user, decode_token
from services.visa_agent import run_visa_agent
from services.rag_engine import load_knowledge_base
from db.database import delete_appointment
from db.database import (
    init_db, get_all_tasks, get_all_clients, get_dashboard_stats,
    update_task_status, update_task_status_by_trello_url,
    get_task_trello_url, get_all_appointments, get_user_by_email,
    update_user_profile, get_chat_history
)
from services.trello_service import move_trello_card
from dotenv import load_dotenv

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

# Initialize on startup
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

    db_user = get_user_by_email(user["email"])
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
    history = get_chat_history(user["user_id"], limit=60)
    return history

# ============================
# 📅 APPOINTMENTS
# ============================
@app.get("/appointments")
async def get_appointments(user=Depends(get_current_user)):
    if not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin only")
    return get_all_appointments()

# ============================
# 💬 ORIGINAL CHAT (DS Tech)
# ============================
@app.post("/chat")
async def chat(data: dict):
    message = data.get("message", "").strip()
    user_id = data.get("user_id", "web_user")
    channel = data.get("channel", "web")
    if not message:
        return {"response": "⚠️ Please send a valid message"}
    response = run_agent(message, user_id=user_id, channel=channel)
    return {"response": response}

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

@app.patch("/tasks/{task_id}")
async def update_task(task_id: int, data: dict):
    new_status = data.get("status", "pending")
    update_task_status(task_id, new_status)
    trello_url = get_task_trello_url(task_id)
    if trello_url:
        move_trello_card(trello_url, new_status)
    return {"success": True}

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
        entry        = data["entry"][0]
        changes      = entry["changes"][0]
        value        = changes["value"]
        if "messages" not in value:
            return {"status": "no message"}
        message_data = value["messages"][0]
        from_number  = message_data["from"]
        if message_data.get("type") != "text":
            send_whatsapp_message(from_number, "Sorry, I can only process text messages.")
            return {"status": "non-text"}
        user_message = message_data["text"]["body"]
        response     = run_agent(user_message, user_id=f"wa_{from_number}", channel="whatsapp")
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
        data        = await request.json()
        action      = data.get("action", {})
        if action.get("type") != "updateCard":
            return {"status": "ignored"}
        card_data   = action.get("data", {})
        card        = card_data.get("card", {})
        list_after  = card_data.get("listAfter", {})
        if not list_after:
            return {"status": "no list change"}
        card_url    = f"https://trello.com/c/{card.get('shortLink', '')}"
        list_name   = list_after.get("name", "").lower()
        status_map  = {"to do": "pending", "doing": "in_progress", "in progress": "in_progress", "done": "done"}
        new_status  = status_map.get(list_name)
        if new_status:
            update_task_status_by_trello_url(card_url, new_status)
    except Exception as e:
        print(f"❌ Trello webhook error: {e}")
    return {"status": "ok"}

@app.post("/whatsapp/webhook")
async def whatsapp_webhook(request: Request):
    data = await request.json()
    try:
        entry        = data["entry"][0]
        changes      = entry["changes"][0]
        value        = changes["value"]
        if "messages" not in value:
            return {"status": "no message"}

        message_data = value["messages"][0]
        from_number  = message_data["from"]

        if message_data.get("type") != "text":
            send_whatsapp_message(from_number, "Sorry, I can only process text messages.")
            return {"status": "non-text"}

        user_message = message_data["text"]["body"]
        print(f"📱 WhatsApp from {from_number}: {user_message}")

        # ✅ Get integer client ID
        client_id = get_or_create_client(
            name=f"WA {from_number}",
            channel="whatsapp",
            phone=from_number
        )

        user_data = {
            "name":   f"WA {from_number}",
            "email":  "",
            "cgpa":   "",
            "degree": "",
            "phone":  from_number,
        }

        # ✅ Pass integer client_id directly
        response = run_visa_agent(user_message, user_id=int(client_id), user_data=user_data)
        send_whatsapp_message(from_number, response)

    except Exception as e:
        print(f"❌ WhatsApp error: {e}")
    return {"status": "ok"}
@app.delete("/appointments/{appointment_id}")
async def delete_appt(appointment_id: int, user=Depends(get_current_user)):
    if not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin only")
    success = delete_appointment(appointment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return {"success": True}




from db.database import (
    delete_client, update_appointment_status,
    add_client_manual, get_all_users
)
from services.trello_service import move_trello_card

# Delete client
@app.delete("/clients/{client_id}")
async def delete_client_endpoint(client_id: int):
    from db.database import delete_client
    success = delete_client(client_id)
    if not success:
        raise HTTPException(status_code=400, detail="Could not delete client")
    return {"success": True}

# Add client manually
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

# Get registered users (portal signups)
@app.get("/users")
async def get_users():
    return get_all_users()

# Update appointment status + sync Trello
@app.patch("/appointments/{appt_id}")
async def update_appointment(appt_id: int, data: dict):
    new_status = data.get("status")
    trello_url = update_appointment_status(appt_id, new_status)
    if trello_url and new_status == "done":
        move_trello_card(trello_url, "done")
    return {"success": True}

# Delete appointment
@app.delete("/appointments/{appt_id}")
async def delete_appointment(appt_id: int):
    db = SessionLocal()
    try:
        appt = db.query(Appointment).filter(Appointment.id == appt_id).first()
        if appt:
            db.delete(appt)
            db.commit()
        return {"success": True}
    finally:
        db.close()