import logging
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


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
    logger.info(f"Subscription was deleted for admin {admin_id}")

    bots = await db.admin_api.get_admins_bots(session, admin_id)
    for index, bot in enumerate(bots, 1):
        if index > 2:
            await db.bot_api.delete_bot(session, bot.id)
            logger.info(f"Bot {bot.id} was deleted from DB")
            continue

        await db.bot_api.update_bot_field(session, bot.id, "is_premium", False)
        await db.bot_api.update_bot_field(session, bot.id, "post_formatting", None)
        await db.bot_api.update_bot_field(session, bot.id, "start_message", None)
        await db.bot_api.update_bot_field(session, bot.id, "answer_message", None)
        logger.info(
            f"Status is_premium and post formatting were deleted for bot {bot.id}"
        )

        admins = await db.bot_api.get_bots_admins(session, bot.id)
        for co_admin_id in admins[1:]:
            await db.bot_api.remove_admin(session, bot.id, co_admin_id)
            logger.info(f"Admin {co_admin_id} was deleted for bot {bot.id}")
