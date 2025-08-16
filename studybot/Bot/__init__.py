from pyrogram import Client
from config import *

# Initialize the main study bot client
studybot = Client(
    name=SESSION,
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="plugins"),
    workers=100
)

# Initialize the content bot client
content_bot = Client(
    name="ContentBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=CONTENT_BOT_TOKEN,
    plugins=dict(root="plugins"),
    workers=50
)

# Global clients dictionary
clients = {
    "main": studybot,
    "content": content_bot
}
