import sys
import glob
import importlib
from pathlib import Path
from pyrogram import Client, idle, __version__
from pyrogram.raw.all import layer
import time
from pyrogram.errors import FloodWait
import asyncio
from datetime import date, datetime
import pytz
from aiohttp import web
import logging
import logging.config

# Import study bot specific modules
from database.study_db import init_db
from config import *
from utils import temp
from Script import script
from plugins import web_server, check_expired_premium, keep_alive

# Import study bot clients
from studybot.Bot import studybot
from studybot.util.keepalive import ping_server
from studybot.Bot.clients import initialize_clients

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("aiohttp").setLevel(logging.ERROR)
logging.getLogger("aiohttp.web").setLevel(logging.ERROR)
logging.getLogger("pymongo").setLevel(logging.WARNING)

botStartTime = time.time()
ppath = "plugins/*.py"
files = glob.glob(ppath)

async def studybot_start():
    """Initialize and start the Study Bot"""
    print('\n\nInitializing Study Bot')
    
    # Initialize database
    await init_db()
    
    # Start study bot
    await studybot.start()
    bot_info = await studybot.get_me()
    studybot.username = bot_info.username
    
    # Initialize clients
    await initialize_clients()
    
    # Load plugins
    for name in files:
        with open(name) as a:
            patt = Path(a.name)
            plugin_name = patt.stem.replace(".py", "")
            plugins_dir = Path(f"plugins/{plugin_name}.py")
            import_path = "plugins.{}".format(plugin_name)
            spec = importlib.util.spec_from_file_location(import_path, plugins_dir)
            load = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(load)
            sys.modules["plugins." + plugin_name] = load
            print("Study Bot Imported => " + plugin_name)
    
    # Start keep alive if on Heroku
    if ON_HEROKU:
        asyncio.create_task(ping_server())
    
    # Set bot info
    me = await studybot.get_me()
    temp.ME = me.id
    temp.U_NAME = me.username
    temp.B_NAME = me.first_name
    temp.B_LINK = me.mention
    studybot.username = '@' + me.username
    
    # Start premium check task
    studybot.loop.create_task(check_expired_premium(studybot))
    
    # Log startup
    logging.info(f"{me.first_name} with Pyrogram v{__version__} (Layer {layer}) started on {me.username}.")
    logging.info(script.LOGO)
    
    # Send restart message to log channel
    tz = pytz.timezone('Asia/Kolkata')
    today = date.today()
    now = datetime.now(tz)
    time_str = now.strftime("%H:%M:%S %p")
    await studybot.send_message(chat_id=LOG_CHANNEL, text=script.RESTART_TXT.format(temp.B_LINK, today, time_str))
    
    # Start web server
    app = web.AppRunner(await web_server())
    await app.setup()
    bind_address = "0.0.0.0"
    await web.TCPSite(app, bind_address, PORT).start()
    
    # Start keep alive
    studybot.loop.create_task(keep_alive())
    
    # Start idle
    await idle()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    while True:
        try:
            loop.run_until_complete(studybot_start())
            break  
        except FloodWait as e:
            print(f"FloodWait! Sleeping for {e.value} seconds.")
            time.sleep(e.value) 
        except KeyboardInterrupt:
            logging.info('Study Bot Service Stopped Bye 👋')
            break
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            time.sleep(5)
