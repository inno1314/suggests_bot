from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, cast, BigInteger
from typing import Any

from .base_class import BaseDBApi
from .model import SuggestedMessage
from utils import generate_id


class MessageDatabaseApi(BaseDBApi):
    async def add_message(self, session: AsyncSession,
                          message_id: int, sender_id: int,
                          chat_id: int, bot_id: int,
                          data: Any, html_text: str,
                          media_group_id: str | None = '',
                          group_id: str | None = None):
        """
        Добавляет предложенное сообщение в БД

        :param message_id: Telegram ID сообщения
        :param sender_id: Telegram ID отправителя
        :param data: JSON дамп модели
        :param html_text: форматированный текст сообщения
        :param chat_id: Telegram ID чата
        :param bot_id: Telegram ID бота
        """
        if group_id is None:
            group_id = generate_id()
        message = SuggestedMessage(
            id = message_id,
            chat_id = chat_id,
            media_group_id=media_group_id,
            group_id = group_id,
            sender_id=sender_id,
            bot_id=bot_id,
            html_text=html_text,
            message_data=data
        )
        session.add(message)
        await session.commit()

    async def get_message(self, session: AsyncSession,
                          message_id: int) -> SuggestedMessage:
        """
        Находит выбранное сообщение в БД

        :param message_id: Telegram ID сообщения
        """
        query = select(SuggestedMessage).where(SuggestedMessage.id == message_id)
        message: SuggestedMessage = await session.scalar(query)
        return message

    async def get_messages_by_media_group_id(self, session: AsyncSession,
                                       bot_id: int,
                                       chat_id: int,
                                       media_group_id: str) -> list[SuggestedMessage]:
        """
        Возвращает список ID сообщений из предложки

        :param bot_id: Telegram ID бота с предложкой
        :param chat_id: Telegram ID чата, в который была отправлена медиагруппа
        :param media_group_id: Media Group ID 
        :return: все сообщения
        """
        query = select(SuggestedMessage).where(
            SuggestedMessage.bot_id == bot_id,
            SuggestedMessage.chat_id == chat_id,
            SuggestedMessage.media_group_id == media_group_id)
        result = await session.execute(query)
        group = result.scalars().all()
        
        return group

    async def get_messages_by_group_id(self, session: AsyncSession,
                                       bot_id: int,
                                       group_id: str) -> list[SuggestedMessage]:
        """
        Возвращает список ID сообщений из предложки

        :param bot_id: Telegram ID бота с предложкой
        :param group_id: Group ID 
        :return: все сообщения
        """
        query = select(SuggestedMessage).where(SuggestedMessage.bot_id == bot_id, \
                                                  SuggestedMessage.group_id == group_id)
        result = await session.execute(query)
        group = result.scalars().all()
        
        return group

    async def delete_suggested_msg(self, session: AsyncSession,
                                   message_id: int):
        """
        Удаляет выбранное сообщение из БД

        :param message_id: Telegram ID сообщения
        """
        query = select(SuggestedMessage).where(SuggestedMessage.id == message_id)
        result = await session.scalar(query)
        await session.delete(result)
        await session.flush()
        await session.commit()

    async def get_suggests(self, session: AsyncSession,
                           sender_id: int) -> list[SuggestedMessage]:
        """
        Возвращает список всех сообщений в предложке от конкретного отправителя

        :param sender_id: Telegram ID отправителя
        """
        query = select(SuggestedMessage).where(SuggestedMessage.sender_id == sender_id)
        result = await session.execute(query)
        messages = result.scalars().all()
        return messages

    async def clean_feed(self, session: AsyncSession,
                         bot_id: int) -> list[SuggestedMessage]:
        """
        Удаляет из БД все сообщения предложки

        :param bot_id: Telegram ID бота с предложкой
        :return: ID всех сообщений
        """
        query = select(SuggestedMessage).where(SuggestedMessage.bot_id == bot_id)
        result = await session.execute(query)
        feed = result.scalars().all()

        ids = [message.id for message in feed]

        query_to_delete = select(SuggestedMessage).where(SuggestedMessage.id.in_(ids))
        result_to_delete = await session.execute(query_to_delete)
        messages_to_delete = result_to_delete.scalars().all()

        for message in messages_to_delete:
            print(f"deleting from db: {message.id}")
            await session.delete(message)

        await session.flush()
        await session.commit()
        return feed

    async def get_active_bots_count(self, session: AsyncSession, days: int = 30) -> int:
        import time
        min_timestamp = time.time() - (days * 86400)
        stmt = (
            select(func.count(func.distinct(SuggestedMessage.bot_id)))
            .where(
                cast(SuggestedMessage.message_data.op("->>")("date"), BigInteger) >= min_timestamp
            )
        )
        result = await session.execute(stmt)
        return result.scalar() or 0

    async def get_platform_suggestions_count(self, session: AsyncSession, days: int = 30) -> int:
        import time
        min_timestamp = time.time() - (days * 86400)
        stmt = (
            select(func.count(SuggestedMessage.primary_key))
            .where(
                cast(SuggestedMessage.message_data.op("->>")("date"), BigInteger) >= min_timestamp
            )
        )
        result = await session.execute(stmt)
        return result.scalar() or 0

    async def get_total_suggestions_count(self, session: AsyncSession) -> int:
        stmt = select(func.count(SuggestedMessage.primary_key))
        result = await session.execute(stmt)
        return result.scalar() or 0

    async def get_bot_suggestions_count(self, session: AsyncSession, bot_id: int) -> int:
        stmt = select(func.count(SuggestedMessage.primary_key)).where(SuggestedMessage.bot_id == bot_id)
        result = await session.execute(stmt)
        return result.scalar() or 0

    async def get_bot_unique_senders_count(self, session: AsyncSession, bot_id: int) -> int:
        stmt = select(func.count(func.distinct(SuggestedMessage.sender_id))).where(SuggestedMessage.bot_id == bot_id)
        result = await session.execute(stmt)
        return result.scalar() or 0

    async def get_bot_suggestions_trend(self, session: AsyncSession, bot_id: int, days: int = 30) -> dict:
        import time
        from datetime import date, datetime, timedelta
        today = date.today()
        dates = [today - timedelta(days=i) for i in range(days)]
        dates.reverse()
        trend = {d: 0 for d in dates}
        
        min_timestamp = time.time() - (days * 86400)
        stmt = (
            select(cast(SuggestedMessage.message_data.op("->>")("date"), BigInteger))
            .where(SuggestedMessage.bot_id == bot_id)
            .where(cast(SuggestedMessage.message_data.op("->>")("date"), BigInteger) >= min_timestamp)
        )
        result = await session.execute(stmt)
        for timestamp in result.scalars().all():
            try:
                msg_date = datetime.fromtimestamp(timestamp).date()
                if msg_date in trend:
                    trend[msg_date] += 1
            except Exception as e:
                pass
        return trend

    async def get_platform_suggestions_trend(self, session: AsyncSession, days: int = 30) -> dict:
        import time
        from datetime import date, datetime, timedelta
        today = date.today()
        dates = [today - timedelta(days=i) for i in range(days)]
        dates.reverse()
        trend = {d: 0 for d in dates}
        
        min_timestamp = time.time() - (days * 86400)
        stmt = (
            select(cast(SuggestedMessage.message_data.op("->>")("date"), BigInteger))
            .where(cast(SuggestedMessage.message_data.op("->>")("date"), BigInteger) >= min_timestamp)
        )
        result = await session.execute(stmt)
        for timestamp in result.scalars().all():
            try:
                msg_date = datetime.fromtimestamp(timestamp).date()
                if msg_date in trend:
                    trend[msg_date] += 1
            except Exception as e:
                pass
        return trend


