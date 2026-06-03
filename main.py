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
from config import VK_TOKEN, ADMIN_CHAT_ID


# =========================
# 🌐 FLASK (Railway keep alive)
# =========================

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is alive", 200

@app.route("/health")
def health():
    return "OK", 200


def run_http():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)


threading.Thread(target=run_http, daemon=True).start()


# =========================
# 🤖 VK BOT
# =========================

print("Bot starting...", flush=True)

GROUP_ID = int(os.environ["GROUP_ID"])

vk_session = vk_api.VkApi(token=VK_TOKEN)
vk = vk_session.get_api()

longpoll = VkBotLongPoll(vk_session, GROUP_ID)

print("LongPoll connected", flush=True)
print("Bot started", flush=True)


while True:
    try:
        print("WAITING FOR EVENTS...", flush=True)

        for event in longpoll.listen():

            try:
                if event.type != VkBotEventType.MESSAGE_NEW:
                    continue

                msg = (event.object.message.get("text") or "").strip()
                peer_id = event.object.message["peer_id"]
                user_id = event.object.message["from_id"]
                message_id = event.object.message["id"]

                print(f"MESSAGE: {msg}", flush=True)

                # =========================
                # 🚫 BAD WORD FILTER
                # =========================
                bad_words = get_bad_words()

                if contains_bad_word(msg, bad_words):
                    delete_message(message_id)
                    send_message(peer_id, "⚠ сообщение удалено")
                    continue

                # =========================
                # 🚨 REPORT
                # =========================
                if msg.lower().startswith("/report"):
                    reason = msg[len("/report"):].strip()

                    add_report(peer_id, user_id, msg, reason)

                    # 🔥 защита от VK API ошибок
                    try:
                        send_message(
                            ADMIN_CHAT_ID,
                            f"🚨 Репорт\n"
                            f"Чат: {peer_id}\n"
                            f"От: {user_id}\n"
                            f"Причина: {reason}\n"
                            f"Сообщение: {msg}"
                        )
                    except Exception as e:
                        print("ADMIN SEND ERROR:", repr(e), flush=True)

                    send_message(peer_id, "✅ репорт отправлен")

            except Exception as e:
                print("EVENT ERROR:", repr(e), flush=True)

    except Exception as e:
        print("LOOP ERROR:", repr(e), flush=True)
        time.sleep(3)
