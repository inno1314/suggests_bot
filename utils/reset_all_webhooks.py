import asyncio
import logging
from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.exceptions import TelegramAPIError

from data.config import db, PROXY_URL, OTHER_BOTS_URL
from database.model import Bot as BotModel
from sqlalchemy import select

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("reset_webhooks")


async def reset_bot_webhook(session, bot_db, semaphore):
    async with semaphore:
        bot = Bot(token=bot_db.token, session=session)
        try:
            url = OTHER_BOTS_URL.format(bot_token=bot_db.token)
            await bot.set_webhook(
                url=url,
                ip_address=None,
                allowed_updates=[
                    "message",
                    "callback_query",
                    "my_chat_member",
                    "chat_member",
                ],
            )
            logger.info(f"Successfully set webhook for bot {bot_db.id} ({bot_db.name})")
        except TelegramAPIError as e:
            logger.warning(
                f"Failed to set webhook for bot {bot_db.id} ({bot_db.name}): {e}"
            )
        except Exception as e:
            logger.error(f"Unexpected error for bot {bot_db.id} ({bot_db.name}): {e}")


async def main():
    async with db.session_maker() as session:
        result = await session.execute(select(BotModel).filter(BotModel.is_active))
        bots = result.scalars().all()

    logger.info(f"Found {len(bots)} active bots in database.")

    session_client = AiohttpSession(proxy=PROXY_URL)
    semaphore = asyncio.Semaphore(50)  # 50 одновременных запросов

    tasks = [reset_bot_webhook(session_client, bot, semaphore) for bot in bots]
    await asyncio.gather(*tasks)
    await session_client.close()


if __name__ == "__main__":
    asyncio.run(main())
