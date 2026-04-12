# services/slack_bot.py

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from services.visa_agent import run_visa_agent
from db.database import get_user_by_email, get_or_create_client
import os
from dotenv import load_dotenv

load_dotenv()

app = App(token=os.getenv("SLACK_BOT_TOKEN"))

processed_events = set()

@app.event("message")
def handle_message(event, say):
    if event.get("bot_id") or event.get("subtype"):
        return

    event_id = event.get("client_msg_id") or event.get("ts")
    if event_id in processed_events:
        return
    processed_events.add(event_id)
    if len(processed_events) > 500:
        processed_events.clear()

    text    = event.get("text", "").strip()
    slack_uid = event.get("user", "default")
    if not text:
        return

    # ✅ Use consistent integer ID from DB
    client_id = get_or_create_client(
        name=f"Slack User {slack_uid}",
        channel="slack",
        slack_id=slack_uid
    )

    user_data = {
        "name":   f"Slack User {slack_uid}",
        "email":  "",
        "cgpa":   "",
        "degree": "",
        "phone":  "",
    }

    response = run_visa_agent(text, user_id=client_id, user_data=user_data)
    say(response)
def start_slack_bot():
    handler = SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN"))
    handler.start()