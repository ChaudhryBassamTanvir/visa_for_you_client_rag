# test_trello_card.py

import os
import requests
from dotenv import load_dotenv
load_dotenv()

url = "https://api.trello.com/1/cards"
params = {
    "key": os.getenv("TRELLO_API_KEY"),
    "token": os.getenv("TRELLO_TOKEN"),
    "idList": "69ce483fd98acbd8128e9d9c",
    "name": "Test Task from AI Agent",
    "desc": "Testing Trello card creation"
}

response = requests.post(url, params=params)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")