from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import select, update

from .base_class import BaseDBApi
from .model import Bot, Admin, Sender


class BotDatabaseApi(BaseDBApi):
    async def add_bot(
        self,
        session: AsyncSession,
        bot_id: int,
        name: str,
        language_code: str,
        admin_id: int,
        url: str,
        token: str,
        is_premium: bool | None = False,
    ) -> Bot:
        """
        Добавляет бота в БД

        :param bot_id: Telegram ID Бота
        :param language_code: Языковая настройка
        :param admin_id: Telegram ID администратора (создателя)
        :param url: https://t.me/ (будет добавлено) + username
        :param token: Токен бота
        """
        bot = Bot(
            id=bot_id,
            name=name,
            url="https://t.me/" + url,
            language_code=language_code,
            token=token,
            creator_id=admin_id,
            is_premium=is_premium,
        )

        query = select(Admin).where(Admin.id == admin_id)
        result = await session.execute(query)
        admin = result.scalars().first()
        bot.admins.append(admin)

        session.add(bot)
        await session.commit()
        return bot

    async def get_bot(self, session: AsyncSession, bot_id: int) -> Bot:
        """
        Вовращает бота по ID

        :param bot_id: Telegram ID бота
        :return: Bot
        """
        query = select(Bot).where(Bot.id == bot_id)
        bot: Bot = await session.scalar(query)
        return bot

    async def get_bots_for_mailing(self, session: AsyncSession) -> list[Bot]:
        """
        Возвращает список ботов без статуса is_premium
        """
        query = select(Bot).where(Bot.is_premium == False)
        result: Result = await session.execute(query)
        bots = result.scalars().all()
        return bots

    async def get_senders_for_mailing(
        self, session: AsyncSession, bot_id: int
    ) -> list[int]:
        """
        Возвращает список ID пользователей для рассылки
        :param bot_id: Telegram ID бота
        """
        query = (
            select(Bot).options(selectinload(Bot.suggesters)).where(Bot.id == bot_id)
        )
        result: Result = await session.execute(query)
        bot = result.scalars().one()
        return [s.id for s in bot.suggesters if s.is_active]

    async def delete_bot(self, session: AsyncSession, bot_id: int) -> None:
        """
        Удаляет бота по его Telegram ID

        :param bot_id: Telegram ID бота
        :return:
        """
        query = select(Bot).where(Bot.id == bot_id)
        result: Bot = await session.scalar(query)
        await session.delete(result)
        await session.flush()
        await session.commit()

    async def update_bot_field(
        self, session: AsyncSession, bot_id: int, field_name: str, new_value
    ) -> None:
        """
        Обновляет произвольное поле бота в базе данных.

        :param session: Сессия базы данных.
        :param bot_id: ID бота для обновления.
        :param field_name: Имя поля, которое нужно обновить.
        :param new_value: Новое значение для поля.
        """
        query = update(Bot).where(Bot.id == bot_id).values({field_name: new_value})

        await session.execute(query)
        await session.commit()

    async def get_bots_admins(self, session: AsyncSession, bot_id: int) -> list[int]:
        """
        Получает Telegram ID администраторов бота

        :param bot_id: Telegram ID бота
        :return: список чисел
        """
        query = select(Bot).options(selectinload(Bot.admins)).where(Bot.id == bot_id)
        result: Result = await session.execute(query)
        bot: Bot = result.scalars().first()
        admins = [admin.id for admin in bot.admins if admin.is_active]
        return admins

    async def get_banlist(self, session: AsyncSession, bot_id: int) -> list[int]:
        """
        Возвращает список заблокированных пользователей бота
        :param bot_id: Telegram ID бота
        """
        query = select(Bot).where(Bot.id == bot_id)
        result: Result = await session.execute(query)
        bot: Bot = result.scalars().first()
        return bot.banlist

    async def add_admin(self, session: AsyncSession, bot_id: int, admin_id: int):
        """
        Добавляет администратора существующему боту

        :param bot_id: Telegram ID Бота
        :param admin_id: Telegram ID администратора
        """
        query = select(Bot).options(selectinload(Bot.admins)).where(Bot.id == bot_id)
        result: Result = await session.execute(query)
        bot: Bot = result.scalars().first()

        query = select(Admin).where(Admin.id == admin_id)
        result = await session.execute(query)
        admin = result.scalars().first()
        bot.admins.append(admin)  # change to admins.remove for delete
        await session.commit()

    async def remove_admin(self, session: AsyncSession, bot_id: int, admin_id: int):
        """
        Удаляет пользователя из списка администраторов

        :param bot_id: Telegram ID Бота
        :param admin_id: Telegram ID администратора
        """
        query = select(Bot).options(selectinload(Bot.admins)).where(Bot.id == bot_id)
        result: Result = await session.execute(query)
        bot: Bot = result.scalars().first()

        query = select(Admin).where(Admin.id == admin_id)
        result = await session.execute(query)
        admin = result.scalars().first()
        bot.admins.remove(admin)
        await session.commit()

    async def change_user_status(
        self, session: AsyncSession, user_id: int, new_status: bool
    ):
        # Проверяем, находится ли пользователь в таблице Admin
        query = select(Admin).where(Admin.id == user_id)
        result = await session.execute(query)
        admin = result.scalar_one_or_none()

        if admin:
            # Обновляем статус администратора
            query = (
                update(Admin)
                .where(Admin.id == user_id)
                .values({"is_active": new_status})
            )
        else:
            # Проверяем, находится ли пользователь в таблице Senders
            query = select(Sender).where(Sender.id == user_id)
            result = await session.execute(query)
            sender = result.scalar_one_or_none()

            if sender:
                # Обновляем статус отправителя
                query = (
                    update(Sender)
                    .where(Sender.id == user_id)
                    .values({"is_active": new_status})
                )
            else:
                # Если пользователь не найден ни в одной из таблиц, можно выбросить исключение или вернуть False
                print("User not found in both tables")

        await session.execute(query)
        await session.commit()

    async def get_all_users_for_ads(self, session: AsyncSession) -> list["Sender"]:

        query = (
            select(Bot)
            .where(Bot.is_premium == False, Bot.is_active == True)
            .options(joinedload(Bot.suggesters))
        )
        result = await session.execute(query)
        bots = result.scalars().unique().all()  # Добавлен вызов unique()

        active_senders = [s for bot in bots for s in bot.suggesters if s.is_active]
        return active_senders
