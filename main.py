import os
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from dotenv import load_dotenv

load_dotenv()

VK_TOKEN = os.getenv("VK_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID"))

# ВАЖНО: это peer_id беседы (2000000000 + chat_id)
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))

vk_session = vk_api.VkApi(token=VK_TOKEN)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, GROUP_ID)


def send_admin(text):
    print("➡️ TRY SEND TO ADMIN CHAT:", ADMIN_CHAT_ID)

    try:
        vk.messages.send(
            peer_id=ADMIN_CHAT_ID,
            message="🚨 РЕПОРТ:\n" + text,
            random_id=0
        )
        print("✅ ADMIN SEND OK")

    except Exception as e:
        print("❌ ADMIN SEND ERROR:", repr(e))


print("BOT STARTED")

for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        msg = event.object.message
        text = msg.get("text", "")
        peer_id = msg.get("peer_id")

        print("📩 MSG:", text)

        if text.startswith("/report"):
            report = text.replace("/report", "").strip()

            if not report:
                report = "пустой репорт"

            send_admin(f"От чата: {peer_id}\nТекст: {report}")

            vk.messages.send(
                peer_id=peer_id,
                message="❌ репорт сохранён",
                random_id=0
            )
