import os
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from dotenv import load_dotenv

load_dotenv()

VK_TOKEN = os.getenv("VK_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID"))
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))

vk_session = vk_api.VkApi(token=VK_TOKEN)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, GROUP_ID)


def send_admin(message):
    try:
        vk.messages.send(
            peer_id=ADMIN_CHAT_ID,
            message="🚨 РЕПОРТ:\n" + message,
            random_id=0
        )
    except Exception as e:
        print("ADMIN SEND ERROR:", e)


print("BOT STARTED")

for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        msg = event.object.message
        text = msg.get("text", "")
        peer_id = msg.get("peer_id")

        print("MSG:", text)

        if text.startswith("/report"):
            report = text.replace("/report", "").strip()

            if not report:
                report = "пустой репорт"

            send_admin(f"От чата: {peer_id}\nТекст: {report}")

            vk.messages.send(
                peer_id=peer_id,
                message="❌ репорт сохранён, но админу не ушёл",
                random_id=0
            )
if __name__ == "__main__":
    main()
