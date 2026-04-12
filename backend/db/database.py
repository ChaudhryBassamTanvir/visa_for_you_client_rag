# db/database.py

import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from dotenv import load_dotenv
from sqlalchemy import Boolean

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# ============================
# 📦 MODELS
# ============================

class Client(Base):
    __tablename__ = "clients"
    id              = Column(Integer, primary_key=True, autoincrement=True)
    name            = Column(String(100), nullable=False)
    email           = Column(String(100))
    phone           = Column(String(30))
    company         = Column(String(100))
    channel         = Column(String(20))  # slack / whatsapp / web
    slack_id        = Column(String(50))
    created_at      = Column(DateTime, default=datetime.utcnow)
    tasks           = relationship("Task", back_populates="client")
    messages        = relationship("Message", back_populates="client")

class Task(Base):
    __tablename__ = "tasks"
    id              = Column(Integer, primary_key=True, autoincrement=True)
    description     = Column(Text, nullable=False)
    status          = Column(String(20), default="pending")   # pending / in_progress / done
    trello_url      = Column(String(255))
    client_id       = Column(Integer, ForeignKey("clients.id"), nullable=True)
    created_at      = Column(DateTime, default=datetime.utcnow)
    client          = relationship("Client", back_populates="tasks")

class Message(Base):
    __tablename__ = "messages"
    id              = Column(Integer, primary_key=True, autoincrement=True)
    client_id       = Column(Integer, ForeignKey("clients.id"), nullable=True)
    role            = Column(String(10))   # user / ai
    content         = Column(Text)
    channel         = Column(String(20))  # slack / whatsapp / web
    created_at      = Column(DateTime, default=datetime.utcnow)
    client          = relationship("Client", back_populates="messages")

# ============================
# 🔧 INIT DB
# ============================

def init_db():
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")

# ============================
# 📝 TASK FUNCTIONS
# ============================

def create_task(description: str, trello_url: str = "", client_id: int = None):
    db = SessionLocal()
    try:
        task = Task(
            description=description,
            trello_url=trello_url,
            client_id=client_id,
            status="pending"
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        print(f"✅ Task saved to DB: {task.id}")
        return task
    finally:
        db.close()

def get_all_tasks():
    db = SessionLocal()
    try:
        tasks = db.query(Task).order_by(Task.created_at.desc()).all()
        return [
            {
                "id": t.id,
                "description": t.description,
                "status": t.status,
                "trello_url": t.trello_url,
                "client": t.client.name if t.client else "Unknown",
                "created_at": t.created_at.strftime("%b %d, %Y %H:%M") if t.created_at else ""
            }
            for t in tasks
        ]
    finally:
        db.close()

def update_task_status(task_id: int, status: str):
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if task:
            task.status = status
            db.commit()
    finally:
        db.close()


def update_task_status_by_trello_url(trello_url: str, status: str):
    db = SessionLocal()
    try:
        # Match by partial URL since Trello sends short links
        tasks = db.query(Task).all()
        for task in tasks:
            if task.trello_url and trello_url in task.trello_url:
                task.status = status
                db.commit()
                print(f"✅ Task {task.id} status → {status}")
                return True
        print(f"⚠️ No task found for Trello URL: {trello_url}")
        return False
    finally:
        db.close()

# ============================
# 👤 CLIENT FUNCTIONS
# ============================

def get_or_create_client(name: str, channel: str, phone: str = "", email: str = "", slack_id: str = ""):
    db = SessionLocal()
    try:
        # Find existing client by slack_id or phone
        if channel == "slack" and slack_id:
            client = db.query(Client).filter(Client.slack_id == slack_id).first()
        else:
            client = db.query(Client).filter(Client.phone == phone, Client.channel == channel).first()

        if not client:
            client = Client(
                name=name, phone=phone, channel=channel,
                email=email, slack_id=slack_id
            )
            db.add(client)
            db.commit()
            db.refresh(client)
        else:
            # Update name/email if they provided it this time
            if name and name != "Unknown":
                client.name  = name
                client.email = email or client.email
                db.commit()

        return client.id
    finally:
        db.close()

def get_all_clients():
    db = SessionLocal()
    try:
        clients = db.query(Client).order_by(Client.created_at.desc()).all()
        return [
            {
                "id":              c.id,
                "name":            c.name,
                "email":           c.email or "",
                "phone":           c.phone or "",
                "company":         c.company or "",
                "channel":         c.channel,
                "task_count":      len(c.tasks),
                "created_at":      c.created_at.strftime("%b %d, %Y") if c.created_at else "",
                "whatsapp_number": c.phone if c.channel == "whatsapp" else "",
                "slack_id":        c.slack_id or "",   # ✅ real Slack ID now
            }
            for c in clients
        ]
    finally:
        db.close()

# ============================
# 💬 MESSAGE FUNCTIONS
# ============================

def save_message(role: str, content: str, channel: str, client_id: int = None):
    db = SessionLocal()
    try:
        msg = Message(role=role, content=content, channel=channel, client_id=client_id)
        db.add(msg)
        db.commit()
    finally:
        db.close()

def get_dashboard_stats():
    db = SessionLocal()
    try:
        total_tasks    = db.query(Task).count()
        total_clients  = db.query(Client).count()
        pending_tasks  = db.query(Task).filter(Task.status == "pending").count()
        done_tasks     = db.query(Task).filter(Task.status == "done").count()
        return {
            "total_tasks": total_tasks,
            "total_clients": total_clients,
            "pending_tasks": pending_tasks,
            "done_tasks": done_tasks
        }
    finally:
        db.close()

def get_all_clients():
    db = SessionLocal()
    try:
        clients = db.query(Client).order_by(Client.created_at.desc()).all()
        return [
            {
                "id":         c.id,
                "name":       c.name,
                "email":      c.email or "",
                "phone":      c.phone or "",
                "company":    c.company or "",
                "channel":    c.channel,
                "task_count": len(c.tasks),
                "created_at": c.created_at.strftime("%b %d, %Y") if c.created_at else "",
                # Channel-specific fields
                "whatsapp_number": c.phone if c.channel == "whatsapp" else "",
                "slack_id":        c.phone if c.channel == "slack" else "",  
                # "slack_id": c.slack_id or "",
                # "whatsapp_number": c.phone if c.channel == "whatsapp" else "",
            }
            for c in clients
        ]
    finally:
        db.close()

# Add to Client model in database.py
slack_id = Column(String(50))  # stores Slack user ID

# Update get_or_create_client
def get_or_create_client(name: str, channel: str, phone: str = "", email: str = "", slack_id: str = ""):
    db = SessionLocal()
    try:
        if channel == "slack":
            client = db.query(Client).filter(Client.slack_id == slack_id).first()
        else:
            client = db.query(Client).filter(Client.phone == phone, Client.channel == channel).first()

        if not client:
            client = Client(name=name, phone=phone, channel=channel, email=email, slack_id=slack_id)
            db.add(client)
            db.commit()
            db.refresh(client)
        return client.id
    finally:
        db.close()

def get_task_trello_url(task_id: int) -> str:
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        return task.trello_url if task else ""
    finally:
        db.close()




# Add these models to database.py

class User(Base):
    __tablename__ = "users"
    id         = Column(Integer, primary_key=True, autoincrement=True)
    name       = Column(String(100), nullable=False)
    email      = Column(String(100), unique=True, nullable=False)
    password   = Column(String(255), nullable=False)
    is_admin   = Column(Boolean, default=False)
    cgpa       = Column(String(10))
    degree     = Column(String(100))
    phone      = Column(String(30))
    created_at = Column(DateTime, default=datetime.utcnow)
    messages   = relationship("ChatMessage", back_populates="user")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id         = Column(Integer, primary_key=True, autoincrement=True)
    user_id    = Column(Integer, ForeignKey("users.id"))
    role       = Column(String(10))   # user / ai
    content    = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    user       = relationship("User", back_populates="messages")

class Appointment(Base):
    __tablename__ = "appointments"
    id              = Column(Integer, primary_key=True, autoincrement=True)
    user_id         = Column(Integer, ForeignKey("users.id"), nullable=True)
    client_name     = Column(String(100))
    client_email    = Column(String(100))
    client_phone    = Column(String(30))
    preferred_date  = Column(String(50))
    preferred_time  = Column(String(50))
    purpose         = Column(Text)
    status          = Column(String(20), default="pending")
    trello_url      = Column(String(255))
    created_at      = Column(DateTime, default=datetime.utcnow)

# Add these functions to database.py

def create_user(name: str, email: str, hashed_password: str, is_admin: bool = False):
    db = SessionLocal()
    try:
        user = User(name=name, email=email, password=hashed_password, is_admin=is_admin)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    finally:
        db.close()

def get_user_by_email(email: str):
    db = SessionLocal()
    try:
        return db.query(User).filter(User.email == email).first()
    finally:
        db.close()

def update_user_profile(user_id: int, cgpa: str, degree: str, phone: str):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.cgpa   = cgpa
            user.degree = degree
            user.phone  = phone
            db.commit()
    finally:
        db.close()

def save_chat_message(user_id: int, role: str, content: str):
    db = SessionLocal()
    try:
        msg = ChatMessage(user_id=user_id, role=role, content=content)
        db.add(msg)
        db.commit()
    finally:
        db.close()

def get_chat_history(user_id: int, limit: int = 60):
    db = SessionLocal()
    try:
        msgs = db.query(ChatMessage)\
                 .filter(ChatMessage.user_id == user_id)\
                 .order_by(ChatMessage.created_at.desc())\
                 .limit(limit).all()
        msgs.reverse()
        return [{"role": m.role, "content": m.content, "created_at": m.created_at.strftime("%H:%M")} for m in msgs]
    finally:
        db.close()

def create_appointment(client_name: str, client_email: str, client_phone: str,
                        preferred_date: str, preferred_time: str, purpose: str,
                        trello_url: str = "", user_id: int = None):
    db = SessionLocal()
    try:
        appt = Appointment(
            user_id=user_id,
            client_name=client_name,
            client_email=client_email,
            client_phone=client_phone,
            preferred_date=preferred_date,
            preferred_time=preferred_time,
            purpose=purpose,
            trello_url=trello_url
        )
        db.add(appt)
        db.commit()
        db.refresh(appt)
        return appt
    finally:
        db.close()
def get_all_appointments():
    db = SessionLocal()
    try:
        appts = db.query(Appointment).order_by(Appointment.created_at.desc()).all()
        return [
            {
                "id":             a.id,
                "client_name":    a.client_name,
                "client_email":   a.client_email,
                "client_phone":   a.client_phone,
                "preferred_date": a.preferred_date,
                "preferred_time": a.preferred_time,
                "purpose":        a.purpose,
                "status":         a.status,
                "trello_url":     a.trello_url,
                "created_at":     a.created_at.strftime("%b %d, %Y %H:%M") if a.created_at else ""
            }
            for a in appts
        ]
    finally:
        db.close()


def delete_appointment(appointment_id: int):
    db = SessionLocal()
    try:
        appt = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if appt:
            db.delete(appt)
            db.commit()
            return True
        return False
    finally:
        db.close()

def get_all_clients():
    db = SessionLocal()
    try:
        # Get from clients table
        clients = db.query(Client).order_by(Client.created_at.desc()).all()
        result  = [
            {
                "id":              c.id,
                "name":            c.name,
                "email":           c.email or "",
                "phone":           c.phone or "",
                "company":         c.company or "",
                "channel":         c.channel,
                "task_count":      len(c.tasks),
                "created_at":      c.created_at.strftime("%b %d, %Y") if c.created_at else "",
                "whatsapp_number": c.phone if c.channel == "whatsapp" else "",
                "slack_id":        c.slack_id or "",
            }
            for c in clients
        ]

        # Also include web users (from users table) as clients
        users = db.query(User).filter(User.is_admin == False).order_by(User.created_at.desc()).all()
        for u in users:
            result.append({
                "id":              f"u_{u.id}",
                "name":            u.name,
                "email":           u.email or "",
                "phone":           u.phone or "",
                "company":         "",
                "channel":         "web",
                "task_count":      0,
                "created_at":      u.created_at.strftime("%b %d, %Y") if u.created_at else "",
                "whatsapp_number": "",
                "slack_id":        "",
            })

        return result
    finally:
        db.close()



def delete_client(client_id: int):
    db = SessionLocal()
    try:
        # Delete related messages and tasks first
        db.query(ChatMessage).filter(ChatMessage.user_id == client_id).delete()
        db.query(Message).filter(Message.client_id == client_id).delete()
        db.query(Task).filter(Task.client_id == client_id).delete()
        db.query(Appointment).filter(Appointment.user_id == client_id).delete()
        db.query(Client).filter(Client.id == client_id).delete()
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"❌ Delete client error: {e}")
        return False
    finally:
        db.close()

def update_appointment_status(appointment_id: int, status: str):
    db = SessionLocal()
    try:
        appt = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if appt:
            appt.status = status
            db.commit()
            return appt.trello_url
        return ""
    finally:
        db.close()

def add_client_manual(name: str, email: str, phone: str, company: str,
                       channel: str, university: str = "", target_country: str = "",
                       cgpa: str = "", degree: str = ""):
    db = SessionLocal()
    try:
        client = Client(
            name=name, email=email, phone=phone, company=company,
            channel=channel, created_at=datetime.utcnow()
        )
        db.add(client)
        db.commit()
        db.refresh(client)
        return client.id
    finally:
        db.close()

def get_all_users():
    db = SessionLocal()
    try:
        users = db.query(User).filter(User.is_admin == False).order_by(User.created_at.desc()).all()
        return [
            {
                "id":         u.id,
                "name":       u.name,
                "email":      u.email,
                "phone":      u.phone or "",
                "cgpa":       u.cgpa or "",
                "degree":     u.degree or "",
                "created_at": u.created_at.strftime("%b %d, %Y") if u.created_at else "",
            }
            for u in users
        ]
    finally:
        db.close()