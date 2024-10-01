from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .base_class import BaseDBApi
from .model import Channels

class ChannelDatabaseApi(BaseDBApi):
    async def add_channel(self, session: AsyncSession,
                          channel_id: int, name: str, bot_id: int) -> None:
        """
        Добавляет канал в базу данных

        :param channel_id: Telegram ID канала
        :param name: Название канала
        :param bot_id: Telegram ID бота
        """
        channel = Channels(
            id=channel_id,
            name=name,
            bot_id=bot_id
        )
        session.add(channel)
        await session.commit()

    async def get_channel(self, session: AsyncSession,
                          channel_id: int, bot_id: int) -> Channels:
        """
        Получает название канала из базы данных

        :param channel_id: Telegram ID канала
        :param bot_id: Telegram ID бота
        """
        query = select(Channels).where(Channels.id == channel_id, Channels.bot_id == bot_id)
        channel: Channels = await session.scalar(query)
        return channel

    
    async def remove_channel(self, session: AsyncSession,
                          channel_id: int, bot_id: int) -> None:
        """
        Удаляет канал из базы данных

        :param channel_id: Telegram ID канала
        :param bot_id: Telegram ID бота
        """
        query = select(Channels).where(Channels.id == channel_id, Channels.bot_id == bot_id)
        result: Channels = await session.scalar(query)
        await session.delete(result)
        await session.flush()
        await session.commit()

    async def get_channels_info(self, session: AsyncSession,
                               bot_id: int) -> list[dict]:
        """
        Возвращает информацию о каналах, в которых бот указан администратором

        :param bot_id: Telegram ID бота
        :return: Список словарей с ключами 'id', 'name'
        """
        query = select(Channels).where(Channels.bot_id == bot_id)
        result = await session.execute(query)
        channels = result.scalars().all()
        return [{'id': channel.id, 'name': channel.name} for channel in channels]

