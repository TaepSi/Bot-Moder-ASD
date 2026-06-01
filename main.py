import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

from vk import send_message, delete_message
from db import get_bad_words, add_report
from filters import contains_bad_word
from config import VK_TOKEN, ADMIN_CHAT_ID

vk_session = vk_api.VkApi(token=VK_TOKEN)
longpoll = VkLongPoll(vk_session)

print("Bot started...")

for event in longpoll.listen():

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
