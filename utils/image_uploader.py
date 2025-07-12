import requests, io
from PIL import Image
from aiogram.types import Message

from data import config


def image_uploader(message: Message) -> str | None:
    URI_INFO = f"https://api.telegram.org/bot{config.BOT_TOKEN}/getFile?file_id="
    URI = f"https://api.telegram.org/file/bot{config.BOT_TOKEN}/"

    photo_file_id = message.photo[-1].file_id
    response = requests.get(URI_INFO + photo_file_id)
    web_image_path = response.json()["result"]["file_path"]
    img = requests.get(URI + web_image_path)
    img = Image.open(io.BytesIO(img.content))

    img_path = "/root/suggests_bot_dev/ad.png"
    img.save(img_path, format="PNG")

    # Загружаем изображение на Imgur
    with open(img_path, "rb") as f:
        headers = {"Authorization": f"Client-ID {config.IMGUR_CLIENT_ID}"}
        response = requests.post(
            "https://api.imgur.com/3/image", headers=headers, files={"image": f}
        ).json()

        # Проверка успешности запроса
        if response["success"]:
            return response["data"]["link"]
        else:
            return None
