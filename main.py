import os
import time
import threading
import vk_api
import random
from flask import Flask
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

from vk import send_message, delete_message
from db import get_bad_words, add_report
from filters import contains_bad_word


# =========================
# CONFIG
# =========================

VK_TOKEN = os.environ["VK_TOKEN"]
GROUP_ID = int(os.environ["GROUP_ID"])
ADMIN_CHAT_ID = int(os.environ["ADMIN_CHAT_ID"])


# =========================
# FLASK
# =========================

app = Flask(__name__)

@app.route("/")
def home():
    return "OK", 200


def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run, daemon=True).start()


# =========================
# VK BOT
# =========================

print("BOT STARTED")

vk_session = vk_api.VkApi(token=VK_TOKEN)
vk = vk_session.get_api()

longpoll = VkBotLongPoll(vk_session, GROUP_ID)

while True:
    for event in longpoll.listen():

        if event.type != VkBotEventType.MESSAGE_NEW:
            continue

        msg = (event.object.message.get("text") or "").strip()
        peer_id = event.object.message["peer_id"]
        user_id = event.object.message["from_id"]
        message_id = event.object.message["id"]

        print("MSG:", msg)

        # =========================
        # BAD WORDS
        # =========================
        try:
            bad_words = get_bad_words()

            if contains_bad_word(msg, bad_words):
                delete_message(message_id)
                send_message(peer_id, "⚠ удалено")
                continue
        except:
            pass

        # =========================
        # REPORT
        # =========================
        if msg.lower().startswith("/report"):

            reason = msg.replace("/report", "").strip()

            add_report(peer_id, user_id, msg, reason)

            # 🔥 ВАЖНО: тест без падений
            try:
                send_message(
                    ADMIN_CHAT_ID,
                    f"РЕПОРТ\n{peer_id}\n{user_id}\n{reason}\n{msg}"
                )
                send_message(peer_id, "репорт отправлен")
            except Exception as e:
                print("ADMIN ERROR:", repr(e))
                send_message(peer_id, "репорт сохранён, но не отправился админу")
