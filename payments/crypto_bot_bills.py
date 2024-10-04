import logging, time, asyncio

from aiocryptopay import AioCryptoPay, Networks
from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession

from data.config import db, CRYPTO_BOT_TOKEN
from data.messages import messages
from keyboards.inline import create_link_keyboard
from payments.successful_payment import successful_payment


logger = logging.getLogger(__name__)

async def process_crypto_payment(session: AsyncSession, call: types.CallbackQuery,
                                 price: int, plan: str):
    """
    Проверяет оплату в CryptoBot
    :param call: aiogram.types.CallbackQuery
    :param price: Сумма создаваемого платежа
    """
    admin_id = call.from_user.id
    crypto = AioCryptoPay(token=CRYPTO_BOT_TOKEN, network=Networks.MAIN_NET)
    await db.admin_api.assign_admin_label(session, admin_id, "crypto")

    invoice = await crypto.create_invoice(amount=float(price),
                                          fiat='RUB',
                                          currency_type='fiat')
    markup = await create_link_keyboard(invoice.bot_invoice_url)

    msg = await call.message.edit_text(text='<i>❔ Нажми на кнопку ниже чтобы перейти к оплате. </i>',
                                       reply_markup=markup)

    start_time = time.time()
    while time.time() - start_time < 60:  # Проверяем в течение 5 минут
        await asyncio.sleep(30)  # Ждем 30 секунд перед следующей проверкой
        try:
            users_data = await db.admin_api.get_admin(session, admin_id)
            label = users_data.label

            if label != 'crypto':
                await crypto.close()
                return

            invoice_info = await crypto.get_invoices(invoice_ids=invoice.invoice_id)
            status = invoice_info.status
            if status == 'paid':
                await successful_payment(session, admin_id, msg, plan)
                await crypto.close()
                return
            elif status == 'expired':
                await db.admin_api.assign_admin_label(session, admin_id, "None")
                await msg.edit_text('Покупка отменена')
                await crypto.close()
                return
            logger.info(f'Проверка статуса платежа в сервисе crypto_bot')
        except Exception as e:
            logger.info(f"Ошибка при проверке статуса платежа: {e}")

    await msg.edit_text(
        text=messages['ru']['failed_payment'],
        disable_web_page_preview=True)
    await crypto.close()
