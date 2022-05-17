from functools import wraps

from requests import JSONDecodeError, get
from telethon import Button, TelegramClient, events
from telethon.errors.rpcerrorlist import UserNotParticipantError
from dotenv import load_dotenv
from config import *
from database import *
load_dotenv()
###########################################  CLIENT FUNCS ################

kuki = TelegramClient("KUKIBOT", APP_ID, APP_HASH).start(bot_token=BOT_TOKEN)


########################################### HANDLER AND RYTS CHK #########


def cmd(**args):
    args["pattern"] = "^(?i)[/!]" + args["pattern"] + f"(?: |$|{BOT_USERNAME})(.*)"

    def decorator(func):
        kuki.add_event_handler(func, events.NewMessage(**args))
        return func

    return decorator


def cbk(**args):
    def decorator(func):
        kuki.add_event_handler(func, events.CallbackQuery(**args))
        return func

    return decorator


def ryts(func):
    @wraps(func)
    async def admin_check(e):
        try:
            perms = await e.client.get_permissions(e.chat_id, e.sender_id)
            if not perms.is_admin:
                return await e.reply("You are not an admin!")
            elif not perms.change_info:
                return await e.reply("You don't have permission to change info!")
            elif e.is_private:
                return await e.reply("You can't use this command in a private chat!")
            else:
                return await func(e)
        except (UserNotParticipantError, ValueError):
            return await e.reply("You are not in this chat!")

    return admin_check


def aichat(func):
    @wraps(func)
    async def ai_check(e):
        if e.is_private:
            await func(e)
        elif Chat.is_ai_chat(e.chat_id):
            await func(e)
        else:
            return

    return ai_check


############################################# API CHAT ###################


class CONV:
    def __init__(self):
        self.bot = BOT_NAME
        self.owner = OWNER
        self.token = KUKI_TOKEN
        self.url = "https://kukiapi.xyz/api"

    def message(self, text):
        try:
            txt = get(
                self.url
                + f"/apikey={self.token}/{self.bot}/{self.owner}/message={text}",
                timeout=10,
            )
            return txt.json()["reply"]
        except (JSONDecodeError, TimeoutError):
            return "KUKI is not responding. Try again later."
        except Exception as e:
            return e


########################################## MSG HANDLERS ##################


@cmd(pattern="start")
async def start(e):
    await e.reply("hey, I'm {}, a chatbot for Telegram.\n".format(BOT_NAME))


@cmd(pattern="setchat")
@ryts
async def setchat(e):
    if e.is_private:
        await e.reply("This command can't be used in private chats.")
        return
    buttons = Button.inline(
        "Enable", data="enable_{}".format(e.sender_id)
    ), Button.inline("Disable", data="disable_{}".format(e.sender_id))
    await e.reply("AI chat setup", buttons=buttons)


@cbk(pattern="enable_(.*)")
async def enable_ai(e):
    user = int(e.pattern_match.group(1))
    await kuki.get_permissions(e.chat_id, e.sender_id)
    if not user == e.sender_id:
        return await e.answer("You ain't the one who used this command.", alert=True)
    elif Chat.is_ai_chat(e.chat_id):
        return await e.edit("AI is already enabled in this chat.")
    await e.edit(
        "Successfully enabled Kuki Ai in **{}** by [{}](tg://user?id={})".format(
            e.chat.title, e.sender.first_name, e.sender_id
        )
    )
    Chat.add_chat(e.chat_id)


@cbk(pattern="disable_(.*)")
async def disable_ai(e):
    user = int(e.pattern_match.group(1))
    await kuki.get_permissions(e.chat_id, e.sender_id)
    if not user == e.sender_id:
        return await e.answer("You aint the one who used this command.", alert=True)
    elif not Chat.is_ai_chat(e.chat_id):
        return await e.edit("AI is already disabled in this chat.")
    await e.edit(
        "Successfully disabled Kuki Ai in **{}** by [{}](tg://user?id={})".format(
            e.chat.title, e.sender.first_name, e.sender_id
        )
    )
    Chat.rm_chat(e.chat_id)


@kuki.on(
    events.NewMessage(incoming=True, func=lambda x: bool(x.mentioned) or x.is_private)
)
@aichat
async def kuki_handler(e):
    c = CONV()
    if e.text.startswith("/start"):
        return
    await e.reply(c.message(e.raw_text))


################################## INITIALIZATION ########################

kuki.run_until_disconnected()
print("KUKI AI IS NOW ONLINE\n\nCONTACT @METAVOIDSUPPORT FOR QUERIES")
