from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from data.messages import messages

async def is_main_admin(call: CallbackQuery, session: AsyncSession,
                        db, bot_id: int) -> bool:
    """
    Проверяет, является ли пользователь главным администратором
    """
    bot = await db.bot_api.get_bot(session, bot_id)

    if call.from_user.id != bot.creator_id:
        await call.answer(messages['ru']['not_main_admin'],
                          show_alert=True)
        return False
    return True

