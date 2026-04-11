# register_trello_webhook.py
import requests
import os
from dotenv import load_dotenv
load_dotenv()

CLOUDFLARE_URL = "https://exanthematic-reynalda-untamely.ngrok-free.dev"
FULL_BOARD_ID  = "69ce483fd98acbd8128e9d87"  # ✅ paste the long ID here

res = requests.post(
    f"https://api.trello.com/1/webhooks?key={os.getenv('TRELLO_API_KEY')}&token={os.getenv('TRELLO_TOKEN')}",
    json={
        "callbackURL": f"{CLOUDFLARE_URL}/trello/webhook",
        "idModel": FULL_BOARD_ID,
        "description": "DS Technologies task sync"
    }
)
print(f"Status: {res.status_code}")
print(f"Response: {res.text}")