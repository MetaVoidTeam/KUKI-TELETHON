from pymongo import MongoClient

from config import MONGO_DB_URL

kuki_db = MongoClient(MONGO_DB_URL)["KUKI"]["CHATS"]


class Chat:
    def __init__(self, chat_id):
        self.chat_id = chat_id

    def is_ai_chat(chat_id):
        if kuki_db.find_one({"chat_id": chat_id}):
            return True
        else:
            return False

    def add_chat(chat_id):
        if not Chat.is_ai_chat(chat_id):
            kuki_db.insert_one({"chat_id": chat_id})
        else:
            return

    def rm_chat(chat_id):
        if Chat.is_ai_chat(chat_id):
            kuki_db.delete_one({"chat_id": chat_id})
        else:
            return
