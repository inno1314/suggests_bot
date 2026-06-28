import logging
from datetime import date
from sqlalchemy import update, func
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
        service: Literal["aaio", "cryptobot", "plat_card", "plat_sbp"],
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

    async def get_successful_payments_revenue(self, session: AsyncSession) -> float:
        result = await session.execute(
            select(func.sum(Payments.amount)).where(Payments.status == 'successful')
        )
        value = result.scalar()
        return float(value) if value is not None else 0.0

    async def get_successful_payments_by_service(self, session: AsyncSession) -> dict[str, float]:
        result = await session.execute(
            select(Payments.service, func.sum(Payments.amount))
            .where(Payments.status == 'successful')
            .group_by(Payments.service)
        )
        return {row[0]: float(row[1]) for row in result.all()}

    async def get_payment_conversion_rate(self, session: AsyncSession) -> float:
        total_result = await session.execute(select(func.count(Payments.payment_id)))
        total = total_result.scalar() or 0
        if total == 0:
            return 0.0
        successful_result = await session.execute(
            select(func.count(Payments.payment_id)).where(Payments.status == 'successful')
        )
        successful = successful_result.scalar() or 0
        return (successful / total) * 100

    async def get_daily_revenue_trend(self, session: AsyncSession, days: int = 30) -> dict[date, tuple[float, float]]:
        from datetime import datetime, timedelta
        today = date.today()
        dates = [today - timedelta(days=i) for i in range(days)]
        dates.reverse()
        trend = {d: (0.0, 0.0) for d in dates}
        
        result = await session.execute(
            select(Payments.amount, Payments.date, Payments.status)
        )
        for amount, date_str, status in result.all():
            try:
                p_date = datetime.strptime(date_str, "%d.%m.%Y").date()
                if p_date in trend:
                    succ, unsucc = trend[p_date]
                    if status == 'successful':
                        trend[p_date] = (succ + float(amount), unsucc)
                    else:
                        trend[p_date] = (succ, unsucc + float(amount))
            except Exception as e:
                logger.warning(f"Failed to parse payment date string '{date_str}': {e}")
        return trend

    async def get_latest_payments(self, session: AsyncSession, limit: int = 10) -> list[Payments]:
        from datetime import datetime
        result = await session.execute(select(Payments))
        payments = list(result.scalars().all())
        
        def get_parsed_date(p):
            try:
                return datetime.strptime(p.date, "%d.%m.%Y")
            except:
                return datetime.min
                
        payments.sort(key=get_parsed_date, reverse=True)
        return payments[:limit]
