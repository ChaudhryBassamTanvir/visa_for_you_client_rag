# services/slack_bot.py

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from services.langchain_agent import run_agent, store_slack_id
import os
from dotenv import load_dotenv

load_dotenv()

app = App(token=os.getenv("SLACK_BOT_TOKEN"))

# ✅ Track processed events to avoid duplicates
processed_events = set()

@app.event("message")
def handle_message(event, say):
    # Ignore bot messages
    if event.get("bot_id"):
        return

    # Ignore message edits and deletions
    if event.get("subtype"):
        return

    # ✅ Deduplicate using event client_msg_id or ts
    event_id = event.get("client_msg_id") or event.get("ts")
    if event_id in processed_events:
        print(f"⚠️ Duplicate event ignored: {event_id}")
        return
    processed_events.add(event_id)

    # Keep set small
    if len(processed_events) > 500:
        processed_events.clear()

    text    = event.get("text", "").strip()
    user_id = event.get("user", "default")

    if not text:
        return

    store_slack_id(user_id, slack_user_id=user_id)
    response = run_agent(text, user_id=user_id, channel="slack")
    say(response)

def start_slack_bot():
    handler = SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN"))
    handler.start()