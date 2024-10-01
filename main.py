import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from aiohttp import web
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.default import DefaultBotProperties
from aiogram.webhook.aiohttp_server import (
    SimpleRequestHandler,
    TokenBasedRequestHandler,
    setup_application,
)

from data.config import WEB_SERVER_HOST, WEB_SERVER_PORT, \
                        MAIN_BOT_PATH, OTHER_BOTS_PATH, \
                        BOT_TOKEN, BASE_URL, OTHER_BOTS_PATH, db

from middlewares.session_to_update import Session
from middlewares.album_collector import AlbumsMiddleware

from utils import db_subscriptions_checker

async def on_startup(bot: Bot):
    # await db.drop_db()
    # await db.create_db()
    await bot.set_webhook(f"{BASE_URL}{MAIN_BOT_PATH}",
                          allowed_updates=['message', 'callback_query', 'my_chat_member', 'chat_member'])

    scheduler = AsyncIOScheduler()
    scheduler.add_job(db_subscriptions_checker, 'interval', days=1, args=[bot, db])
    scheduler.start()

session = AiohttpSession()
bot = Bot(token=BOT_TOKEN,
          session=session,
    default=DefaultBotProperties(
        parse_mode="HTML"
        )
    )

def main():
    logging.basicConfig(level=logging.INFO)

    from handlers import main_router, other_routers

    storage = MemoryStorage()

    main_dispatcher = Dispatcher(storage=storage)
    main_dispatcher.include_router(main_router)
    main_dispatcher.startup.register(on_startup)
    main_dispatcher.update.middleware(Session(session_pool=db.session_maker))

    other_bots_dispatcher = Dispatcher(storage=storage)
    other_bots_dispatcher.include_router(other_routers)
    other_bots_dispatcher.update.middleware(Session(session_pool=db.session_maker))
    other_bots_dispatcher.message.middleware(AlbumsMiddleware(2))

    app = web.Application()
    SimpleRequestHandler(dispatcher=main_dispatcher, bot=bot).register(app, path=MAIN_BOT_PATH)

    bot_settings = {"session": session, "parse_mode": ParseMode.HTML}

    TokenBasedRequestHandler(
        dispatcher=other_bots_dispatcher,
        bot_settings=bot_settings,
    ).register(app, path=OTHER_BOTS_PATH)

    setup_application(app, main_dispatcher, bot=bot)
    setup_application(app, other_bots_dispatcher)

    web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)

if __name__ == "__main__":
    main()

