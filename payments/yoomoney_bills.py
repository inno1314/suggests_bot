import time, asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from yoomoney import Quickpay, Client
from aiogram import types

from data.config import db, YOOMONEY_TOKEN
from data.messages import messages
from utils import logger
from keyboards.inline import create_link_keyboard
from payments.successful_payment import successful_payment


async def process_yoomoney_payment(session: AsyncSession, call: types.CallbackQuery,
                                   price: int, plan: str):
    """
    Проверяет оплату в платежке ЮМани
    :param call: aiogram.types.CallbackQuery
    :param price: Сумма создаваемого платежа
    """
    admin_id = call.from_user.id
    start_label = await db.admin_api.assign_admin_label(session, admin_id)

    quick_pay = Quickpay(
        receiver='410017428212005',
        quickpay_form='shop',
        targets='Test',
        paymentType='SB',
        sum=price,
        label=start_label
    )

    markup = await create_link_keyboard(quick_pay.redirected_url)
    msg = await call.message.edit_text(text='<i>❔ Нажми на кнопку ниже чтобы перейти к оплате. </i>',
                                       reply_markup=markup)

    start_time = time.time()
    while time.time() - start_time < 60:  # Проверяем в течение 5 минут
        await asyncio.sleep(30)  # Ждем 30 секунд перед следующей проверкой
        try:
            users_data = await db.admin_api.get_admin(session, admin_id)
            label = users_data.label

            if label != start_label:
                return

            client = Client(YOOMONEY_TOKEN)
            history = client.operation_history(label=label)
            operation = history.operations[-1]
            if operation.status == 'success':
                await successful_payment(session, call, plan)
                return
            logger.info(f'Проверка статуса платежа в сервисе yoomoney')

        except Exception as e:
            logger.info(f"Ошибка при проверке статуса платежа: {e}")

    # Время ожидания истекло
    await msg.edit_text(
        text=messages['ru']['failed_payment'],
        disable_web_page_preview=True)

