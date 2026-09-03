import io
import logging
import requests
from PIL import Image
from aiogram.types import Message

from data import config

logger = logging.getLogger(__name__)


def image_uploader(message: Message) -> str | None:
    try:
        proxies = None
        if config.PROXY_URL:
            proxy = config.PROXY_URL
            if proxy.startswith("socks5://"):
                proxy = proxy.replace("socks5://", "socks5h://", 1)
            proxies = {"http": proxy, "https": proxy}

        URI_INFO = f"https://api.telegram.org/bot{config.BOT_TOKEN}/getFile?file_id="
        URI = f"https://api.telegram.org/file/bot{config.BOT_TOKEN}/"

        photo_file_id = message.photo[-1].file_id
        response = requests.get(URI_INFO + photo_file_id, proxies=proxies, timeout=15)
        file_path = response.json()["result"]["file_path"]
        img_resp = requests.get(URI + file_path, proxies=proxies, timeout=15)
        img = Image.open(io.BytesIO(img_resp.content))

        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format="PNG")
        img_byte_arr.seek(0)

        # Загружаем изображение на Imgur
        headers = {"Authorization": f"Client-ID {config.IMGUR_CLIENT_ID}"}
        upload_resp = requests.post(
            "https://api.imgur.com/3/image",
            headers=headers,
            files={"image": img_byte_arr},
            proxies=proxies,
            timeout=20,
        ).json()

        if upload_resp.get("success"):
            return upload_resp["data"]["link"]
        else:
            logger.error(f"Imgur upload failed: {upload_resp}")
            return None
    except Exception as e:
        logger.error(f"Failed to upload image: {e}")
        return None
