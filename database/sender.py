from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from .base_class import BaseDBApi
from .model import Bot, Sender, SuggestedMessage

class SenderDatabaseApi(BaseDBApi):
    async def add_sender(self, session: AsyncSession,
                       user_id: int, first_name: str, bot_id: int) -> None:
        """
        Добавляет отправителя в БД

        :param user_id: Telegram ID пользователя
        :param first_name: first_name пользователя
        :param bot_id: Telegram ID бота
        """
        sender = Sender(
            id = user_id,
            first_name = first_name,
            bot_id = bot_id
        )
        session.add(sender)
        await session.commit()

    async def add_bot_to_sender(self, session: AsyncSession,
                                sender_id: int, bot_id: int):
        """
        Привязывает нового бота к пользователю
        :param sender_id: Telegram ID отправителя
        :param bot_id: Telegram ID бота
        """
        query = (update(Sender)
            .where(Sender.id == sender_id)
            .values({"bot_id": bot_id})
        )
        await session.execute(query)
        await session.commit()

    async def get_sender(self, session: AsyncSession,
                        sender_id: int) -> Sender:
        """
        Возвращает отправителя по ID

        :param sender_id: Telegram ID отправителя
        """
        query = select(Sender).where(Sender.id == sender_id)
        sender: Sender = await session.scalar(query)
        return sender

    async def get_sender_by_message(self, session: AsyncSession,
                                    message_id: int, bot_id: int) -> Optional[int]:
        """
        Возвращает ID отправителя по ID сообщения

        :param message_id: Telegram ID сообщеня
        """
        query = select(SuggestedMessage).where(
            SuggestedMessage.id == message_id,
            SuggestedMessage.bot_id == bot_id
        )
        message: SuggestedMessage = await session.scalar(query)

        if message is None:
            return None

        return message.sender_id

    async def change_block_status(self, session: AsyncSession,
                                  sender_id: int, bot_id: int) -> None:
        """
        Изменяет статус блокироваки бользователя

        :param sender_id: Telegram ID отправителя
        :param bot_id: Telegram ID бота
        """
        query = select(Bot).where(Bot.id == bot_id)
        result = await session.execute(query)
        bot = result.scalars().first()

        if sender_id not in bot.banlist:
            bot.banlist = bot.banlist + [sender_id]
        else:
            bot.banlist = [id for id in bot.banlist if id != sender_id]

        await session.commit()
