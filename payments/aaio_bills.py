import uuid, time, asyncio, random, string

from AaioAPI import AsyncAaioAPI
from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession

from data.config import db, AAIO_API_KEY, AAIO_SECRET_KEY, AAIO_MERCHANT_ID
from data.messages import messages
from utils import logger
from keyboards.inline import create_link_keyboard
from payments.successful_payment import successful_payment


async def process_aaio_payment(session: AsyncSession, call: types.CallbackQuery,
                               price: int, plan: str):
    """
    Проверяет оплату в платежке aaio
    :param call: aiogram.types.CallbackQuery
    :param price: Сумма создаваемого платежа
    """
    admin_id = call.from_user.id
    letters_and_digits = string.ascii_lowercase + string.digits
    start_label = ''.join(random.sample(letters_and_digits, 10))

    client = AsyncAaioAPI(AAIO_API_KEY, AAIO_SECRET_KEY, AAIO_MERCHANT_ID)
    order_id = str(uuid.uuid4())

    payment_url = await client.create_payment(order_id, price,
                                              description='payment for subscribtion')

    await db.admin_api.assign_admin_label(session, admin_id, start_label)

    markup = await create_link_keyboard(payment_url)
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

            client = AsyncAaioAPI(AAIO_API_KEY, AAIO_SECRET_KEY, AAIO_MERCHANT_ID)
            if await client.is_expired(order_id):
                await db.admin_api.assign_admin_label(session, admin_id, "None")
                await msg.edit_text('Покупка отменена')
                return
            elif await client.is_success(order_id):
                await successful_payment(session, admin_id, msg, plan)
                return
            logger.info(f'Проверка статуса платежа в сервисе aaio')

        except Exception as e:
            logger.info(f"Ошибка при проверке статуса платежа: {e}")

    # Время ожидания истекло
    await msg.edit_text(
        text=messages['ru']['failed_payment'],
        disable_web_page_preview=True)
