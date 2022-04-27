# (c) @AmineSoukara
# This File Is A Part Of: https://github.com/AmineSoukara/Stream-HerokuLogs

import asyncio
import os
import traceback
from os.path import isfile

import heroku3
import urllib3
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import Message

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# get a token from @BotFather
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# The Telegram API things
API_ID = int(os.environ.get("API_ID", 12345))
API_HASH = os.environ.get("API_HASH")
# Get these values from my.telegram.org

# Your ID, Or Channel/Group ID :
ID = int(os.environ.get("ID", 12345))

# Owner Id:
OWNER_ID = int(os.environ.get("OWNER_ID", 12345))

# How Mush Lines Do U Want In One Message? :
LINES = int(os.environ.get("LINES", 1))
TIMEOUT = int(os.environ.get("TIMEOUT", 100))

HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME", None)
HEROKU_API_KEY = os.environ.get("HEROKU_API_KEY", None)
PROCESS_TYPE = os.environ.get("PROCESS_TYPE", "worker")

Alty = Client("Alty-Logs", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)


async def main():
    async with Alty:
        try:

            t = "💬 [INFO] Starting To Stream Logs.."
            print(t)
            await Alty.send_message(OWNER_ID, t)

            while True:

                server = heroku3.from_key(HEROKU_API_KEY)
                app = server.app(HEROKU_APP_NAME)

                lines = []
                for line in app.stream_log(lines=1):
                    txt = line.decode("utf-8")
                    lines.append(txt)

                    if len(lines) >= LINES:
                        print(f"✅️ Lines Reached: {len(lines)}")
                        done = "\n".join(l for l in lines)

                        try:

                            if len(done) > 4096:
                                path = f"logs_{HEROKU_APP_NAME}.txt"
                                with open(path, "w") as f:
                                    f.write(done)
                                await Alty.send_document(ID, path)

                                if isfile(path):
                                    os.remove(path)

                            await Alty.send_message(ID, done)

                        except FloodWait as sec:
                            await asyncio.sleep(sec.value)
                        except Exception as e:
                            print(e)
                        finally:
                            lines.clear()

            await asyncio.sleep(3)

        except FloodWait as sec:
            await asyncio.sleep(sec.value)
        except Exception as e:
            print(e)


def heroku_scale(scale: int):
    try:
        heroku_conn = heroku3.from_key(HEROKU_API_KEY)
        app = heroku_conn.app(HEROKU_APP_NAME)
        app.process_formation()[PROCESS_TYPE].scale(scale)
        check = f"App: {HEROKU_APP_NAME} Has Been Scaled {'⚠️ DOWN' if scale == 0 else '✅️ UP'}."
        print(check)
        return check
    except BaseException:
        traceback.print_exc()
        return "⚠️ Error: " + str(traceback.format_exc())


@Alty.on_message(
    filters.private & filters.command(["dyno_on", "dyno_off"]) & filters.user(OWNER_ID)
)
async def dyno_off_on(_, message: Message):
    cmd = message.command[0]
    msg = await message.reply("• Please Wait!")
    scale = 0 if cmd == "dyno_off" else 1
    check = heroku_scale(scale)
    await msg.edit(check)


@Alty.on_message(
    filters.private & filters.command("dyno_restart") & filters.user(OWNER_ID)
)
async def dyno_restart(_, message: Message):
    msg = await message.reply("• Please Wait!")
    try:
        heroku_x = heroku3.from_key(HEROKU_API_KEY)
        ok = heroku_x.apps()[HEROKU_APP_NAME]
        ok.restart()
        await msg.edit(f"✅️ App: {HEROKU_APP_NAME} Restarted !")
    except BaseException:
        err = "⚠️ Error: " + str(traceback.format_exc())
        await msg.edit(err)


Alty.run(main())
