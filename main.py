from config import *
from telethon import events, TelegramClient
from telethon.errors.rpcerrorlist import UserNotParticipantError
from functools import wraps
from random import choice
from database import *
from requests import JSONDecodeError, get



###########################################  CLIENT FUNCS #####################################################

kuki = TelegramClient("KUKIBOT", APP_ID, APP_HASH).start(bot_token=BOT_TOKEN)




########################################### HANDLER AND RYTS CHK ##############################################


def cmd(**args):
    args["pattern"] = "^(?i)[/!]" + args["pattern"] + f"(?: |$|{BOT_USERNAME})(.*)"

    def decorator(func):
        kuki.add_event_handler(func, events.NewMessage(**args))
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


############################################# API CHAT ########################################################



class CONV:
    def __init__(self):
        self.bot = BOT_NAME
        self.owner = OWNER
        self.token = KUKI_TOKEN
        self.url = "https://kukiapi.xyz/api"
    
    
    def message(self, text):
        try:
            txt = get(self.url + f"/apikey={self.token}/{self.bot}/{self.owner}/message={text}", timeout=10)
            return txt.json()["reply"]
        except (JSONDecodeError, TimeoutError):
            return "KUKI is not responding. Try again later."
        except Exception as e:
            return e




########################################## MSG HANDLERS ######################################################

@cmd(pattern="start")
async def start(e):
    await e.reply("hey, I'm {}, a chatbot for Telegram.\n".format(BOT_NAME))




@cmd(pattern="addchat")
@ryts
async def addchat(e):
    if e.is_private:
        await e.reply("You can't use this command in a private chat!")
        return
    if Chat.is_ai_chat(e.chat_id):
        await e.reply("Kuki Ai is already **enabled!**")
        return
    Chat.add_chat(e.chat_id)
    await e.reply(f"Kuki Ai enabled by [{e.sender.first_name}](tg://user?id={e.sender_id}) in **{e.chat.title}**")




@cmd(pattern="rmchat")
@ryts
async def rmchat(e):
    if e.is_private:
        await e.reply("You can't use this command in private chat!")
        return
    if not Chat.is_ai_chat(e.chat_id):
        await e.reply("Kuki Ai is already **disabled!**")
        return
    Chat.rm_chat(e.chat_id)
    await e.reply(f"Kuki Ai disabled by [{e.sender.first_name}](tg://user?id={e.sender_id}) in **{e.chat.title}**")
    
    


@kuki.on(events.NewMessage(incoming = True, func = lambda x: bool(x.mentioned) or x.is_private))
@aichat
async def kuki_handler(e):
    c = CONV()
    if e.text.startswith("/start"):
        return
    await e.reply(c.message(e.raw_text))


################################## INITIALIZATION ###########################################################

kuki.run_until_disconnected()
print("KUKI AI IS NOW ONLINE\n\nCONTACT @METAVOIDSUPPORT FOR QUERIES")

