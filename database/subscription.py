from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.engine import Result
from datetime import datetime, timedelta, timezone
from typing import Literal

from .base_class import BaseDBApi
from .model import Subscription


class SubscriptionDatabaseApi(BaseDBApi):
    async def add_subscription(
        self,
        session: AsyncSession,
        admin_id: int,
        subscription_type: Literal["month", "three_months", "half_year", "year"],
    ) -> datetime:
        """
        Добавляет подписку в БД

        :param admin_id: Telegram ID администратора
        :param subscription_type: Тип подписки (month, three_months, half_year, year)
        :return: Время окончания подписки
        """
        duration_map = {
            "month": timedelta(days=30),
            "three_months": timedelta(days=90),
            "half_year": timedelta(days=180),
            "year": timedelta(days=365),
        }
        current_sub = await self.get_subscription(session, admin_id)
        if current_sub is None:
            end_date = datetime.now(timezone.utc) + duration_map[subscription_type]
            subscription = Subscription(
                admin_id=admin_id, end_date=end_date, plan=subscription_type
            )
            session.add(subscription)
        else:
            start_time = current_sub.end_date
            end_date = start_time + duration_map[subscription_type]
            query = (
                update(Subscription)
                .where(Subscription.admin_id == admin_id)
                .values(end_date=end_date)
            )
            await session.execute(query)

        await session.commit()
        return end_date

    async def get_subscription(
        self, session: AsyncSession, admin_id: int
    ) -> Subscription | None:
        """
        Проверяет, есть ли у администратора активная подписка

        :param admin_id: Telegram ID администратора
        :return: Subscription если подписка активна, иначе None
        """
        query = select(Subscription).where(
            Subscription.admin_id == admin_id,
            Subscription.end_date > datetime.now(timezone.utc),
        )
        result: Result = await session.execute(query)
        sub: Subscription | None = result.scalars().first()
        return sub

    async def get_all_subscriptions(self, session: AsyncSession) -> list[Subscription]:
        """
        Возвращает все подписки из базы данных

        :param session: Текущая сессия базы данных
        :return: Список всех подписок
        """
        query = select(Subscription)
        result: Result = await session.execute(query)
        subscriptions: list[Subscription] = result.scalars().all()
        return subscriptions

    async def clean_subscriptions(self, session: AsyncSession, admin_id: int):
        """
        Удаляет истекшую подписку администратору
        :param admin_id: Telegram ID администратора
        """
        query = select(Subscription).where(Subscription.admin_id == admin_id)
        result = await session.scalar(query)
        await session.delete(result)
        await session.flush()
        await session.commit()

    async def get_subscription_income(self, session: AsyncSession):
        query = select(Subscription)
        result = await session.execute(query)
        subscriptions = result.scalars().all()

        price_map = {
            "month": 159.0,
            "three_months": 143.0,
            "half_year": 133.0,
            "year": 108.25,
        }
        income = 0

        for sub in subscriptions:
            income += price_map.get(sub.plan, 0.0)

        return income
