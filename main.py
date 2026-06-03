import os
import time
import threading
import vk_api
import random
from flask import Flask
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

from db import get_bad_words, add_report
from filters import contains_bad_word


# =========================
# CONFIG
# =========================

VK_TOKEN = os.environ["VK_TOKEN"]
GROUP_ID = int(os.environ["GROUP_ID"])
ADMIN_CHAT_ID = int(os.environ["ADMIN_CHAT_ID"])


# =========================
# FLASK (Railway)
# =========================

app = Flask(__name__)

@app.route("/")
def home():
    return "OK", 200


def run_http():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_http, daemon=True).start()


# =========================
# VK BOT
# =========================

print("BOT STARTED", flush=True)

vk_session = vk_api.VkApi(token=VK_TOKEN)
vk = vk_session.get_api()

longpoll = VkBotLongPoll(vk_session, GROUP_ID)


def send(peer_id, text):
    vk.messages.send(
        peer_id=peer_id,
        message=text,
        random_id=random.randint(1, 2**31)
    )


while True:
    for event in longpoll.listen():

        if event.type != VkBotEventType.MESSAGE_NEW:
            continue

        msg = (event.object.message.get("text") or "").strip()
        peer_id = event.object.message["peer_id"]
        user_id = event.object.message["from_id"]
        message_id = event.object.message["id"]

        print("MSG:", msg, flush=True)

        # =========================
        # BAD WORDS
        # =========================
        try:
            bad_words = get_bad_words()

            if contains_bad_word(msg, bad_words):
                vk.messages.delete(
                    message_ids=message_id,
                    delete_for_all=1
                )
                send(peer_id, "⚠ сообщение удалено")
                continue
        except Exception as e:
            print("BAD WORD ERROR:", repr(e), flush=True)

        # =========================
        # REPORT
        # =========================
        if msg.lower().startswith("/report"):

            reason = msg[len("/report"):].strip()

            add_report(peer_id, user_id, msg, reason)

            try:
                # 🔥 ПРОСТАЯ ОТПРАВКА (БЕЗ ХИТРОСТЕЙ)
                send(
                    ADMIN_CHAT_ID,
                    f"🚨 РЕПОРТ\n"
                    f"Чат: {peer_id}\n"
                    f"От: {user_id}\n"
                    f"Причина: {reason}\n"
                    f"Сообщение: {msg}"
                )

                send(peer_id, "✅ репорт отправлен")

            except Exception as e:
                print("ADMIN ERROR:", repr(e), flush=True)
                send(peer_id, "❌ репорт сохранён, но админу не ушёл")
