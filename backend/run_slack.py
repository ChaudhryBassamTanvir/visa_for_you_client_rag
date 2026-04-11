from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
import os

from services.slack_bot import app

load_dotenv()

handler = SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN"))

if __name__ == "__main__":
    handler.start()