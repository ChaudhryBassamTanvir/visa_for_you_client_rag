# services/trello_service.py

import os
import requests
from dotenv import load_dotenv
load_dotenv()

# Trello list IDs — must match your board
TRELLO_LISTS = {
    "pending":     "69ce483fd98acbd8128e9d9c",  # To Do
    "in_progress": "69ce483fd98acbd8128e9d9d",  # Doing
    "done":        "69ce483fd98acbd8128e9d9e",  # Done
}

def get_card_id_from_url(card_short_url: str) -> str:
    """Extract card short link and fetch full card ID from Trello"""
    if not card_short_url:
        return ""
    # URL format: https://trello.com/c/SHORTLINK
    short_link = card_short_url.rstrip("/").split("/")[-1]
    url = f"https://api.trello.com/1/cards/{short_link}"
    params = {
        "key": os.getenv("TRELLO_API_KEY"),
        "token": os.getenv("TRELLO_TOKEN"),
        "fields": "id,name"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get("id", "")
    print(f"❌ Could not fetch card ID: {response.status_code} {response.text}")
    return ""

def move_trello_card(card_short_url: str, new_status: str) -> bool:
    """Move a Trello card to the correct list based on status"""
    list_id = TRELLO_LISTS.get(new_status)
    if not list_id:
        print(f"❌ Unknown status: {new_status}")
        return False

    card_id = get_card_id_from_url(card_short_url)
    if not card_id:
        print(f"❌ Could not find Trello card for URL: {card_short_url}")
        return False

    url = f"https://api.trello.com/1/cards/{card_id}"
    params = {
        "key": os.getenv("TRELLO_API_KEY"),
        "token": os.getenv("TRELLO_TOKEN"),
        "idList": list_id
    }
    response = requests.put(url, params=params)
    if response.status_code == 200:
        print(f"✅ Trello card moved to: {new_status}")
        return True
    print(f"❌ Trello move failed: {response.status_code} {response.text}")
    return False