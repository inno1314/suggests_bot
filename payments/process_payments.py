import logging, time, asyncio

from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Literal

from data.config import db
from data.messages import messages
from keyboards.inline import create_link_keyboard
from payments import (
    AsyncYoomoneyAPI,
    AsyncAaioAPI,
    AsyncCryptoPayAPI,
    AsyncNicePayAPI,
)
from payments.successful_payment import successful_payment

logger = logging.getLogger(__name__)

clients = {
    "yoomoney": AsyncYoomoneyAPI(),
    "aaio": AsyncAaioAPI(),
    "cryptobot": AsyncCryptoPayAPI(),
    "nicepay": AsyncNicePayAPI(),
}


async def process_payment(
    session: AsyncSession,
    call: types.CallbackQuery,
    plan: Literal["month", "three_months", "half_year", "year"],
    payment_amount: int,
    system: Literal["yoomoney", "aaio", "cryptobot", "nicepay"],
):
    """
    Проверяет оплату в CryptoBot
    :param call: aiogram.types.CallbackQuery
    :param price: Сумма создаваемого платежа
    :param system: Система, в которой совершается платеж.
    """
    admin_id = call.from_user.id

    client = clients[system]
    url, payment_id = await client.create_payment(amount=payment_amount)
    await db.payments_api.create_payment(
        session,
        user_id=admin_id,
        amount=payment_amount,
        service=system,
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
        logger.info(f"checking {system} payment status from user {admin_id}")
        try:
            async with db.session_maker() as new_session:
                users_data = await db.admin_api.get_admin(new_session, admin_id)
                await new_session.close()
            label = users_data.label
            logger.info(f"\nstart_label: {payment_id}, label: {label}")

            if label != payment_id:
                await client.close()
                logger.info(f"returned from {system} payment: label != start_label")
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
            elif await client.is_expired(payment_id):
                await db.payments_api.change_payment_status(
                    session_pool=db.session_maker,
                    payment_id=payment_id,
                    status="expired",
                )
                await db.admin_api.assign_admin_label(session, admin_id, "None")
                await msg.edit_text(
                    text=messages["failed_payment"], disable_web_page_preview=True
                )
                await client.close()
                logger.info(f"{system} payment from user {admin_id} is expired")
                return
        except Exception as e:
            logger.info(f"exception while checking {system} payment: {e}")

    # Время ожидания истекло
    logger.info(f"timeout for {system} payment from user {admin_id}")
    await client.close()
    await db.payments_api.change_payment_status(
        session_pool=db.session_maker,
        payment_id=payment_id,
        status="expired",
    )
    await msg.edit_text(text=messages["failed_payment"], disable_web_page_preview=True)
