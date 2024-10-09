import logging
from datetime import datetime
from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from data.config import db
from data.messages import messages
from keyboards.inline import sub_types, payment_methods
from states import TopUpBalance
from utils import clean_subscription
from payments import process_payment

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == "get_premium")
async def get_premium(call: types.CallbackQuery, session: AsyncSession):
    sub = await db.subscription_api.get_subscription(
        session, admin_id=call.from_user.id
    )
    end_date = None
    if sub is not None:
        date_object = datetime.strptime(str(sub.end_date), "%Y-%m-%d %H:%M:%S.%f%z")
        end_date = date_object.strftime("%d.%m.%Y %H:%M")
    text = '⭐️<b>Подписка "PRO"</b>\n\n'
    sub_status = (
        "<i><b>не активна</b></i>"
        if end_date is None
        else f"<i><b>активна до {end_date}</b></i>"
    )
    text += f"⏱Теущий статус: {sub_status}\n\n"
    text += messages["about_subscription"]
    await call.message.edit_text(text, reply_markup=sub_types)


@router.callback_query(F.data.in_(["month", "three_months", "half_year", "year"]))
async def set_plan(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(TopUpBalance.balance)
    await state.update_data(plan=str(call.data))
    await call.message.edit_text(
        text=messages["payment_method"], reply_markup=payment_methods
    )
    await call.answer()


@router.callback_query(F.data.in_(["yoomoney", "aaio", "crypto_bot"]))
async def set_pay_method(
    call: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    data = await state.get_data()
    plan = data.get("plan")
    method = call.data

    plan_prices = {"month": 159, "three_months": 429, "half_year": 799, "year": 1299}
    price = plan_prices.get(plan)

    logger.info(f"Chosen options - Plan: {plan}, Method: {method}, Price: {price}")

    await process_payment(
        session=session, call=call, plan=plan, payment_amount=price, payment_type=method
    )

    await state.clear()


@router.callback_query(F.data == "clear_sub")
async def clear_sub(call: types.CallbackQuery, session: AsyncSession):
    admin_id = call.from_user.id
    sub = await db.subscription_api.get_subscription(session, admin_id)
    if sub is None:
        await call.answer(text="Subscription not active", show_alert=True)
        return
    logger.info(
        f"Admin's {admin_id} sub start date: {sub.start_date}, end date: {sub.end_date}"
    )
    await clean_subscription(session, admin_id, db)
    updated_sub = await db.subscription_api.get_subscription(session, admin_id)
    if updated_sub is None:
        logger.info("Subscription was successfully cleaned!")
    await call.answer()
