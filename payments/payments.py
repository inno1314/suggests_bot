import asyncio
import time
from aiogram import Bot, Router, F, types, html
from aiogram.fsm.context import FSMContext
from aiocryptopay import AioCryptoPay, Networks
from yoomoney import Client
from utils import logger
from data.config import payok_transactions_data as payok_info, db, YOOMONEY_TOKEN
from payments import create_yoomoney_payment_link, create_payok_payment_link, successful_payment
from .payok_api import get_transaction
from keyboards.inline import create_link_keyboard

router = Router()


async def process_payment(call: types.CallbackQuery, state: FSMContext, payment_type: str):
    await state.set_state(state=None)
    data = await state.get_data()
    product = data.get('product')

    if payment_type == "payok":
        msg = await create_payok_payment_link(call=call, price=product['price'])
        logger.info(f'Сгенерирована платежная ссылка payok на сумму {product["price"]} рублей')

    elif payment_type == "crypto":
        crypto = AioCryptoPay(token='172004:AA7x04QcC9pdDTlLJI9HBNpMsMcbDNagp9P', network=Networks.MAIN_NET)
        await db.update_value(user_id=call.from_user.id, field='label', value='crypto')
        invoice = await crypto.create_invoice(amount=float(product['price']), fiat='RUB', currency_type='fiat')
        markup = await create_link_keyboard(invoice.bot_invoice_url)
        await bot.delete_message(call.from_user.id, call.message.message_id)
        msg = await bot.send_message(chat_id=call.from_user.id,
                               text='<i>❔ Нажми на кнопку ниже чтобы перейти к оплате. </i>',
                               reply_markup=markup)
        invoice_id = invoice.invoice_id
        logger.info(f'Сгенерирована платежная ссылка crypto_bot на сумму {product["price"]} рублей')

    elif payment_type == "yoomoney":
        msg = await create_yoomoney_payment_link(call=call, price=product['price'])
        logger.info(f'Сгенерирована платежная ссылка yoomoney на сумму {product["price"]} рублей')

    users_data = await db.get_user(user_id=call.from_user.id)
    start_label = users_data['label']

    start_time = time.time()
    while time.time() - start_time < 300:  # Проверяем в течение 5 минут
        await asyncio.sleep(30)  # Ждем 30 секунд перед следующей проверкой
        try:
            users_data = await db.get_user(user_id=call.from_user.id)
            label = users_data['label']

            if label != start_label:
                if payment_type == "crypto":
                    await crypto.close()
                return

            if payment_type == "payok":
                response_data = await get_transaction(API_KEY=payok_info['API_KEY'],
                                                      API_ID=payok_info['API_ID'],
                                                      shop=payok_info['shop'],
                                                      payment=label)
                transaction_status = response_data['1']['transaction_status']
                if transaction_status == '1':
                    await successful_payment(call=call, payment_amount=product['price'], product=product)
                    return
                logger.info(f'Проверка статуса платежа в сервисе payok')
                # await successful_payment(call=call, payment_amount=product['price'], product=product)
                # return

            elif payment_type == "crypto":
                invoice_info = await crypto.get_invoices(invoice_ids=invoice_id)
                status = invoice_info.status
                if status == 'paid':
                    await successful_payment(call=call, payment_amount=product['price'], product=product)
                    await crypto.close()
                    return
                elif status == 'expired':
                    await db.update_value(user_id=call.from_user.id, field='label', value='1')
                    await bot.delete_message(call.from_user.id, call.message.message_id)
                    await bot.send_message(chat_id=call.from_user.id, text='Покупка отменена')
                    # await call.message.answer('Покупка отменена')
                    await crypto.close()
                    return
                logger.info(f'Проверка статуса платежа в сервисе crypto_bot')
                # await successful_payment(call=call, payment_amount=product['price'], product=product)

            elif payment_type == "yoomoney":
                client = Client(YOOMONEY_TOKEN)
                history = client.operation_history(label=label)
                operation = history.operations[-1]
                if operation.status == 'success':
                    await successful_payment(call=call, payment_amount=product['price'], product=product)
                    return
                logger.info(f'Проверка статуса платежа в сервисе yoomoney')

        except Exception as e:
            logger.info(f"Ошибка при проверке статуса платежа: {e}")

    # Время ожидания истекло
    await msg.edit_text(
        text=f"{html.italic('Нам не удалось обработать ваш платеж.')}\n\n"
             f"Пожалуйста, обратитесь к нашему {html.link('менеджеру', 'https://t.me/rtmanageer')}",
        disable_web_page_preview=True)
    # if payment_type == "crypto":
    #     await crypto.close()
    await state.clear()
