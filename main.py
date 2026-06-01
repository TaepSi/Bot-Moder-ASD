import os
import time
import threading
import vk_api
from flask import Flask
from vk_api.longpoll import VkLongPoll, VkEventType

from vk import send_message, delete_message
from db import get_bad_words, add_report
from filters import contains_bad_word
from config import VK_TOKEN, ADMIN_CHAT_ID


# =========================
# 🌐 HTTP SERVER (Railway fix)
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

print("Bot starting...")

vk_session = vk_api.VkApi(token=VK_TOKEN)
longpoll = VkLongPoll(vk_session)

print("LongPoll connected")
print("Bot started...")


while True:
    try:
        print("WAITING FOR EVENTS...", flush=True)

        for event in longpoll.listen():

            try:
                if event.type != VkEventType.MESSAGE_NEW:
                    continue

                msg = event.text or ""
                peer_id = event.peer_id
                user_id = event.user_id
                message_id = event.message_id

                bad_words = get_bad_words()

                # 🚫 автоудаление
                if contains_bad_word(msg, bad_words):
                    delete_message(message_id)
                    send_message(peer_id, "⚠ сообщение удалено")
                    continue

                # 🚨 репорты
                if msg.startswith("/report"):
                    reason = msg.replace("/report", "").strip()

                    add_report(peer_id, user_id, msg, reason)

                    send_message(
                        ADMIN_CHAT_ID,
                        f"🚨 Репорт\nЧат: {peer_id}\nОт: {user_id}\nПричина: {reason}\nСообщение: {msg}"
                    )

            except Exception as e:
                print("EVENT ERROR:", repr(e), flush=True)

    except Exception as e:
        print("LOOP ERROR:", repr(e), flush=True)
        time.sleep(3)
