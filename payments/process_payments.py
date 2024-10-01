import logging
from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession
from payments import process_yoomoney_payment, process_aaio_payment, process_crypto_payment


logger = logging.getLogger(__name__)

async def process_payment(session: AsyncSession,
                          call: types.CallbackQuery,
                          plan: str,
                          payment_amount: int,
                          payment_type: str):

    if payment_type == "aaio":
        logger.info(f'Сгенерирована платежная ссылка aaio на сумму {payment_amount} рублей')
        await process_aaio_payment(session=session,
                                   call=call,
                                   price=payment_amount,
                                   plan=plan)

    elif payment_type == "crypto_bot":
        logger.info(f'Сгенерирована платежная ссылка crypto_bot на сумму {payment_amount} рублей')
        await process_crypto_payment(session=session,
                                     call=call,
                                     price=payment_amount,
                                     plan=plan)

    elif payment_type == "yoomoney":
        logger.info(f'Сгенерирована платежная ссылка yoomoney на сумму {payment_amount} рублей')
        await process_yoomoney_payment(session=session,
                                       call=call,
                                       price=payment_amount,
                                       plan=plan)

