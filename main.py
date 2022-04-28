# (c) @AmineSoukara
# This File Is A Part Of: https://github.com/AmineSoukara/Stream-HerokuLogs

import asyncio
import os
import traceback
from os.path import isfile
import sys
import heroku3
import urllib3
from pyrogram import Client, filters
from pyrogram.errors import (
    ChannelInvalid,
    ChatAdminRequired,
    FloodWait,
    PeerIdInvalid,
    UserIdInvalid,
    UsernameInvalid,
    UsernameNotOccupied,
)
from pyrogram.types import Message
from pyromod.helpers import ikb

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
LINES = int(os.environ.get("LINES", 5))
TIMEOUT = int(os.environ.get("TIMEOUT", 100))
AS_DOC = is_enabled((environ.get("AS_DOC", "False")), False)

HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME", None)
HEROKU_API_KEY = os.environ.get("HEROKU_API_KEY", None)
PROCESS_TYPE = os.environ.get("PROCESS_TYPE", "worker")

Alty = Client("Alty-Logs", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)


async def main():
    async with Alty:
        try:

            t = f"💬 [INFO] Starting To Stream Logs\n\n•APP: {HEROKU_APP_NAME.upper()}\n•LINES: {LINES} Per Message"
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

                            if any([len(done) > 4096, AS_DOC]):
                                path = f"logs_{HEROKU_APP_NAME}.txt"
                                with open(path, "w") as f:
                                    f.write(done)
                                await Alty.send_document(ID, document=path, thumb="./logos/heroku_logo_doc.png")

                                if isfile(path):
                                    os.remove(path)

                            await Alty.send_message(ID, done)

                        except (
                            ChatAdminRequired,
                            PeerIdInvalid,
                            ChannelInvalid,
                            UserIdInvalid,
                            PeerIdInvalid,
                            UsernameInvalid,
                            UsernameNotOccupied,
                            KeyError,
                        ):

                            traceback.print_exc()
                            await Alty.send_message(
                                OWNER_ID,
                                f"⚠️ Ayooo, The User/Channel/Supergroup Is Not Accessible, ID: {ID}",
                            )
                            break
                        except FloodWait as sec:
                            await asyncio.sleep(sec.value)
                        except Exception:
                            traceback.print_exc()
                            err = "⚠️ Error: " + str(traceback.format_exc())
                            await Alty.send_message(OWNER_ID, err)
                            sys.exit()

                        finally:
                            lines.clear()

            # await asyncio.sleep(3)

        except FloodWait as sec:
            await asyncio.sleep(sec.value)
        except Exception:
            traceback.print_exc()


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

def is_enabled(value, default):
    if value.lower() in ["true", "yes", "1", "enable", "y"]:
        return True
    elif value.lower() in ["false", "no", "0", "disable", "n"]:
        return False
    else:
        return default


@Alty.on_message(filters.private & filters.command("start"))
async def start_bot(_, message: Message):
    pic = "https://i.imgur.com/965G4d5.png"
    caption = """
With This Code You Can Stream The Tail: In A Specific Chat (Private / Channel)

• Available Commands:
/dyno_off - /dyno_on - /dyno_restart
"""
    buttons = ikb(
        [
            [
                (
                    "👨‍💻 Developer",
                    "https://t.me/aminesoukara",
                    "url",
                ),
                (
                    "Source Code 🔗",
                    "https://github.com/AmineSoukara/Stream-HerokuLogs",
                    "url",
                ),
            ],
        ]
    )

    await message.reply_photo(pic, caption=caption, reply_markup=buttons)


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
