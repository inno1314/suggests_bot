import logging
from datetime import datetime
from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from data.config import db
from data.messages import messages
from keyboards.inline import sub_types, payment_methods
from states import TopUpBalance
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
    text = '<blockquote><b>🪄 Подписка "PRO"</b></blockquote>\n\n'
    sub_status = (
        "<i>не активна</i>" if end_date is None else f"<i>активна до {end_date}</i>"
    )
    text += f"<b>⏱Теущий статус:</b> {sub_status}\n\n"
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


@router.callback_query(F.data.in_(["aaio", "cryptobot", "plat_card", "plat_sbp"]))
async def set_pay_method(
    call: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    data = await state.get_data()
    plan = data["plan"]
    method = call.data

    plan_prices = {"month": 159, "three_months": 429, "half_year": 799, "year": 1299}
    price = plan_prices.get(plan)

    logger.info(f"Chosen options - Plan: {plan}, Method: {method}, Price: {price}")

    await process_payment(
        session=session,
        call=call,
        state=state,
        plan=plan,
        payment_amount=price,
        payment_operator=method,
    )

    await state.clear()
