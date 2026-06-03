import vk_api
import random
from config import VK_TOKEN

vk_session = vk_api.VkApi(token=VK_TOKEN)
vk = vk_session.get_api()


def send_message(peer_id, text):
    try:
        vk.messages.send(
            peer_id=peer_id,
            message=text,
            random_id=random.randint(1, 2**31)
        )
    except Exception as e:
        print("SEND ERROR:", repr(e), flush=True)
