import logging
from datetime import date
from sqlalchemy import update
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from typing import Literal, Sequence

from .model import Payments
from .base_class import BaseDBApi

logger = logging.getLogger(__name__)


class PaymentsDatabaseAPI(BaseDBApi):
    async def create_payment(
        self,
        session: AsyncSession,
        user_id: int,
        amount: float,
        service: Literal[
            "aaio", "cryptobot", "cryptomus", "freekassa", "nicepay", "yoomoney"
        ],
        payment_id: str,
    ) -> None:
        """
        Добавляет информацию о платеже в базу данных.
        :param user id: Telegram ID пользователя.
        :param amount: Сумма платежа.
        :param service: Сервис платежной системы.
        :param payment_id: Идентификатор платежа.
        :return: payment id.
        """
        today = date.today().strftime("%d.%m.%Y")
        payment = Payments(
            payment_id=payment_id,
            user_id=user_id,
            amount=amount,
            service=service,
            date=today,
        )
        session.add(payment)
        await session.commit()
        logger.info(f"Payment {payment_id} was added to DB")

    async def get_payment_info(
        self, session_pool: async_sessionmaker, payment_id: str
    ) -> Payments | None:
        """
        Возвращает информацию о платеже
        :param payment id: Идентификатор платежа
        """
        async with session_pool() as session:
            query = select(Payments).where(Payments.payment_id == payment_id)
            result = await session.execute(query)
            payment = result.scalar_one_or_none()
            return payment

    async def change_payment_status(
        self,
        session_pool: async_sessionmaker,
        payment_id: str,
        status: Literal["successful", "expired"],
    ):
        """
        Изменяет статус платежа
        :param payment id: ID платежа в БД
        :param status: Статус платежа
        """
        async with session_pool() as session:
            query = (
                update(Payments)
                .where(Payments.payment_id == payment_id)
                .values(status=status)
            )
            await session.execute(query)
            await session.commit()
        logger.info(f"Status of payment {payment_id} was changed to {status}")

    async def get_all_payments(self, session: AsyncSession) -> Sequence[Payments]:
        result = await session.execute(select(Payments))
        return result.scalars().all()
