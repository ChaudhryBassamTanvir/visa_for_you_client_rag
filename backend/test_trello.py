# test_trello.py

import os
import requests
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("TRELLO_API_KEY")
TOKEN = os.getenv("TRELLO_TOKEN")
BOARD_ID = os.getenv("TRELLO_BOARD_ID")

print(f"API Key: {API_KEY[:6]}..." if API_KEY else "❌ API Key missing")
print(f"Token: {TOKEN[:6]}..." if TOKEN else "❌ Token missing")
print(f"Board ID: {BOARD_ID}")

# Test: Get lists from board
url = f"https://api.trello.com/1/boards/{BOARD_ID}/lists"
params = {"key": API_KEY, "token": TOKEN}
response = requests.get(url, params=params)

if response.status_code == 200:
    lists = response.json()
    print(f"\n✅ Trello connected! Found {len(lists)} lists:")
    for l in lists:
        print(f"  - {l['name']} (ID: {l['id']})")
else:
    print(f"\n❌ Trello error: {response.status_code} - {response.text}")