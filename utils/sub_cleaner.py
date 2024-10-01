from sqlalchemy.ext.asyncio import AsyncSession

# from database.base_api import DataBaseApi
from utils import logger

async def clean_subscription(session: AsyncSession, admin_id: int, db):
    """
    Отбирает у пользователя все преимущества платной подписки:
    1. Удаляет данные о подписки из БД
    2. Отнимает у ботов статус is_premium
    3. Удаляет всех ботов администратора, кроме первых двух
    4. Удаляет всех совместных администраторов
    5. Удаляет форматирование постов
    """
    await db.subscription_api.clean_subscriptions(session, admin_id)
    logger.info(f"Данные о подписке администратора {admin_id} удалены")

    bots = await db.admin_api.get_admins_bots(session, admin_id)
    for index, bot in enumerate(bots, 1):
        if index > 2:
            await db.bot_api.delete_bot(session, bot.id)
            logger.info(f"Бот {bot.id} был удален из БД")
            continue

        await db.bot_api.update_bot_field(session, bot.id,
                                          "is_premium", False)
        await db.bot_api.update_bot_field(session, bot.id,
                                      "post_formatting", None)
        logger.info(f"Статус is_premium и оформление сброшены для бота {bot.id}")

        admins = await db.bot_api.get_bots_admins(session, bot.id)
        for co_admin_id in admins[1:]:
            await db.bot_api.remove_admin(session, bot.id, co_admin_id)
            logger.info(f"Администратор {co_admin_id} удален для бота {bot.id}")

