# (c) @AmineSoukara
# This File Is A Part Of: https://github.com/AmineSoukara/Stream-HerokuLogs
 

import os
import re
import heroku3
import urllib3
from pyrogram import Client

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# get a token from @BotFather
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# The Telegram API things
API_ID = int(os.environ.get("APP_ID", 12345))
API_HASH = os.environ.get("API_HASH")
# Get these values from my.telegram.org

# Your ID, Or Channel/Group ID :
ID = int(os.environ.get("ID", 12345))

HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME", None)
HEROKU_API_KEY = os.environ.get("HEROKU_API_KEY", None)


Alty = Client("Alty-Logs", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)


def main():
    with Alty:
        while True:
            try:
                t = "💬 [INFO] Starting To Stream Logs.."
                print(t)
                Alty.send_message(ID, t)
            except Exception as e:
                print(e)

            server = heroku3.from_key(HEROKU_API_KEY)
            app = server.app(HEROKU_APP_NAME)
            for line in app.stream_log(lines=1):
                try:
                    txt = line.decode("utf-8")
                    done = "➕ " + txt
                    Alty.send_message(ID, done)
                except Exception as e:
                    print(e)

#            time.sleep(TIME * 60)


main()
