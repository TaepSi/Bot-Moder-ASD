import time
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

from vk import send_message, delete_message
from db import get_bad_words, add_report
from filters import contains_bad_word
from config import VK_TOKEN, ADMIN_CHAT_ID

print("Bot starting...")

# VK init
vk_session = vk_api.VkApi(token=VK_TOKEN)

try:
    longpoll = VkLongPoll(vk_session)
    print("LongPoll connected")
except Exception as e:
    print("LongPoll ERROR:", repr(e))
    while True:
        time.sleep(60)

print("Bot started...")

# защита от падений (главное исправление)
while True:
    try:
        print("WAITING FOR EVENTS...")

        for event in longpoll.listen():

            try:
                if event.type != VkEventType.MESSAGE_NEW:
                    continue

                msg = event.text or ""
                peer_id = event.peer_id
                user_id = event.user_id
                message_id = event.message_id

                bad_words = get_bad_words()

                # автоудаление
                if contains_bad_word(msg, bad_words):
                    delete_message(message_id)
                    send_message(peer_id, "⚠ сообщение удалено")
                    continue

                # репорт
                if msg.startswith("/report"):
                    reason = msg.replace("/report", "").strip()

                    add_report(peer_id, user_id, msg, reason)

                    send_message(
                        ADMIN_CHAT_ID,
                        f"🚨 Репорт\nЧат: {peer_id}\nОт: {user_id}\nПричина: {reason}\nСообщение: {msg}"
                    )

            except Exception as e:
                print("EVENT ERROR:", repr(e))

    except Exception as e:
        print("LOOP CRASH:", repr(e))
        time.sleep(5)
