from dotenv import load_dotenv
from os import getenv
from aiogram import types

from database.base_api import DataBaseApi

load_dotenv()

WEB_SERVER_HOST = "0.0.0.0"
WEB_SERVER_PORT = 8000
MAIN_BOT_PATH = "/suggests/main"
OTHER_BOTS_PATH = "/suggests/bot/{bot_token}"
BOT_TOKEN = str(getenv("BOT_TOKEN"))
BASE_URL = str(getenv("BASE_URL"))
OTHER_BOTS_URL = f"{BASE_URL}{OTHER_BOTS_PATH}"

DB_URL = "postgresql+asyncpg://inno:root@localhost/suggests_db"

db = DataBaseApi(DB_URL)


other_bots_commands = [
    types.BotCommand(command="/start", description="Запустить нижнее меню"),
    types.BotCommand(command="/rm", description="Очистить предложку"),
    types.BotCommand(command="/help", description="Помощь"),
    types.BotCommand(command="/banlist", description="Список заблокированных юзеров"),
    types.BotCommand(command="/remove_keyboard", description="Удалить нижнее меню"),
]

CREATORS = [575586402, 6435987938]

YOOMONEY_TOKEN = str(getenv("YOOMONEY_TOKEN"))
YOOMONEY_WALLET = str(getenv('YOOMONEY_WALLET'))
UNDRESS_API_KEY = str(getenv("UNDRESS_API_KEY"))
CRYPTO_BOT_TOKEN = str(getenv("CRYPTO_BOT_TOKEN"))
AAIO_API_KEY = str(getenv("AAIO_API_KEY"))
AAIO_MERCHANT_ID = str(getenv("AAIO_MERCHANT_ID"))
AAIO_SECRET_KEY = str(getenv("AAIO_SECRET_KEY"))
NICE_PAY_SECRET_KEY = str(getenv('NICE_PAY_SECRET_KEY'))
NICE_PAY_MERCHANT_ID = str(getenv('NICE_PAY_MERCHANT_ID'))
