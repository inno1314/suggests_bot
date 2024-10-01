from aiogram import types, F, Router
from sqlalchemy.ext.asyncio import AsyncSession

from utils import generate_view_count_chart
from data.config import db
from keyboards.inline import back_markup

router = Router()

@router.callback_query(F.data == "show_incomes")
async def show_incomes(call: types.CallbackQuery, session: AsyncSession):
    income_from_subs = await db.subscription_api.get_subscription_income(session)
    users_for_ad_mailing = await db.bot_api.get_all_users_for_ads(session)
    path, count = await generate_view_count_chart(session)

    caption = f"Месячный доход с подписок: {income_from_subs}\nРассылку увидят "\
         f"{len(users_for_ad_mailing)} пользователей\nПоказов рекламы в ответном "\
         f"сообщении: {count}"

    photo = types.FSInputFile(path)

    await call.message.delete()
    await call.message.answer_photo(photo, caption,
                                    reply_markup=back_markup)
