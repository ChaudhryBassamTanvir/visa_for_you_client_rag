# db/seed.py

from database import init_db, SessionLocal, Client, Task, Message
from datetime import datetime, timedelta
import random

def seed():
    init_db()
    db = SessionLocal()

    try:
        # Clear existing data
        db.query(Message).delete()
        db.query(Task).delete()
        db.query(Client).delete()
        db.commit()

        # Seed clients
        clients_data = [
            {"name": "Ahmed Khan",      "email": "ahmed@example.com",   "phone": "923001234567", "company": "Khan Traders",      "channel": "whatsapp"},
            {"name": "Sara Malik",      "email": "sara@example.com",    "phone": "923009876543", "company": "Malik Enterprises", "channel": "slack"},
            {"name": "John Smith",      "email": "john@example.com",    "phone": "923001112222", "company": "Smith Co",          "channel": "web"},
            {"name": "Fatima Zaidi",    "email": "fatima@example.com",  "phone": "923003334444", "company": "Zaidi Group",       "channel": "whatsapp"},
            {"name": "Usman Raza",      "email": "usman@example.com",   "phone": "923005556666", "company": "Raza Tech",         "channel": "slack"},
        ]

        clients = []
        for c in clients_data:
            client = Client(**c, created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30)))
            db.add(client)
            clients.append(client)

        db.commit()
        for c in clients:
            db.refresh(c)

        # Seed tasks
        tasks_data = [
            {"description": "Build restaurant website with online menu",         "status": "pending",     "trello_url": "https://trello.com/c/abc1", "client": clients[0]},
            {"description": "Mobile app for delivery tracking",                  "status": "in_progress", "trello_url": "https://trello.com/c/abc2", "client": clients[1]},
            {"description": "AI chatbot for customer support",                   "status": "done",        "trello_url": "https://trello.com/c/abc3", "client": clients[2]},
            {"description": "E-commerce platform with payment integration",      "status": "pending",     "trello_url": "https://trello.com/c/abc4", "client": clients[3]},
            {"description": "Company portfolio website redesign",                "status": "in_progress", "trello_url": "https://trello.com/c/abc5", "client": clients[4]},
            {"description": "WhatsApp automation bot for order management",      "status": "pending",     "trello_url": "https://trello.com/c/abc6", "client": clients[0]},
            {"description": "Dashboard for sales analytics",                     "status": "done",        "trello_url": "https://trello.com/c/abc7", "client": clients[1]},
        ]

        for t in tasks_data:
            task = Task(
                description=t["description"],
                status=t["status"],
                trello_url=t["trello_url"],
                client_id=t["client"].id,
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 20))
            )
            db.add(task)

        db.commit()
        print("✅ Seed complete! Clients and tasks added.")

    finally:
        db.close()

if __name__ == "__main__":
    seed()