import os
import requests
import io
from PIL import Image
from aiogram.types import Message


def image_uploader(message: Message, token: str) -> str | None:

    URI_INFO = f"https://api.telegram.org/bot{token}/getFile?file_id="
    URI = f"https://api.telegram.org/file/bot{token}/"

    photo_file_id = message.photo[-1].file_id
    response = requests.get(URI_INFO + photo_file_id)
    web_image_path = response.json()["result"]["file_path"]
    img = requests.get(URI + web_image_path)
    img = Image.open(io.BytesIO(img.content))
    img.save("/root/suggest_bot/ad.png", format="PNG")

    with open("/root/suggest_bot/ad.png", "rb") as f:
        response = requests.post(
            "https://telegra.ph/upload", files={"file": ("file", f, "ad.png")}
        ).json()

        if "error" in response:
            print(f'Ошибка при загрузке изображения на Telegra.ph: {response["error"]}')
            return None
        else:
            # os.remove(web_image_path)
            return "telegra.ph" + response[0]["src"]
