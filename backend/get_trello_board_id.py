# get_trello_board_id.py
import requests, os
from dotenv import load_dotenv
load_dotenv()

res = requests.get(
    f"https://api.trello.com/1/boards/{os.getenv('TRELLO_BOARD_ID')}",
    params={"key": os.getenv("TRELLO_API_KEY"), "token": os.getenv("TRELLO_TOKEN"), "fields": "id,name"}
)
print(res.json())