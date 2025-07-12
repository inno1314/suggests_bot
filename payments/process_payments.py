import logging, time, asyncio

from aiogram import types
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Literal

from data.config import db
from data.messages import messages
from keyboards.inline import create_link_keyboard
from payments import AsyncAaioAPI, AsyncCryptoPayAPI, AsyncPlatAPI
from payments.successful_payment import successful_payment

logger = logging.getLogger(__name__)

clients = {
    "aaio": AsyncAaioAPI(),
    "cryptobot": AsyncCryptoPayAPI(),
    "plat_sbp": AsyncPlatAPI(method="sbp"),
    "plat_card": AsyncPlatAPI(method="card"),
}


async def process_payment(
    session: AsyncSession,
    call: types.CallbackQuery,
    state: FSMContext,
    plan: Literal["month", "three_months", "half_year", "year"],
    payment_amount: int,
    payment_operator: Literal["aaio", "cryptobot", "plat_card", "plat_sbp"],
):
    """
    Проверяет оплату во всех платежных системах.
    :param call: aiogram.types.CallbackQuery
    :param price: Сумма создаваемого платежа
    :param system: Система, в которой совершается платеж.
    """
    admin_id = call.from_user.id

    client = clients[payment_operator]
    url, payment_id = await client.create_payment(
        amount=payment_amount, user_id=admin_id
    )
    if url == payment_id == "ERROR":
        return await call.answer(
            text="⚠️ Не удалось найти реквизиты! Попробуйте другую сумму, другой метод оплаты или повторите через несколько минут.",
            show_alert=True,
        )

    await state.clear()

    await db.payments_api.create_payment(
        session,
        user_id=admin_id,
        amount=payment_amount,
        service=payment_operator,
        payment_id=payment_id,
    )
    await db.admin_api.assign_admin_label(
        session=session, admin_id=admin_id, label=payment_id
    )

    markup = await create_link_keyboard(url)
    msg = await call.message.edit_text(
        text=messages["start_payment"],
        reply_markup=markup,
        disable_web_page_preview=True,
    )

    start_time = time.time()
    while time.time() - start_time < 600:  # Проверяем в течение 10 минут
        await asyncio.sleep(30)  # Ждем 30 секунд перед следующей проверкой
        logger.info(f"Checking {payment_operator} payment status from user {admin_id}")
        try:
            async with db.session_maker() as new_session:
                users_data = await db.admin_api.get_admin(new_session, admin_id)
                await new_session.close()
            label = users_data.label

            if label != payment_id:
                await client.close()
                logger.info(
                    f"Return from {payment_operator} payment: label != start_label"
                )
                await db.payments_api.change_payment_status(
                    session_pool=db.session_maker,
                    payment_id=payment_id,
                    status="expired",
                )
                return

            if await client.is_success(payment_id):
                await client.close()
                await db.payments_api.change_payment_status(
                    session_pool=db.session_maker,
                    payment_id=payment_id,
                    status="successful",
                )
                return await successful_payment(
                    admin_id=admin_id, session=session, message=call.message, plan=plan
                )
        except Exception as e:
            logger.info(f"Exception while checking {payment_operator} payment: {e}")

    # Время ожидания истекло
    logger.info(f"Timeout for {payment_operator} payment from user {admin_id}")
    await client.close()
    await db.payments_api.change_payment_status(
        session_pool=db.session_maker,
        payment_id=payment_id,
        status="expired",
    )
    await msg.edit_text(text=messages["failed_payment"], disable_web_page_preview=True)
