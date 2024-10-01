import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.engine import Result
from sqlalchemy.orm import selectinload

from .base_class import BaseDBApi
from .model import Admin, Bot

class AdminDatabaseApi(BaseDBApi):
    async def add_admin(self, session: AsyncSession,
                        admin_id: int,
                        name: str | None = "no name",
                        language_code: str | None = "en") -> Admin:
        """
        Добавляет администратора в БД

        :param admin_id: Telegram ID пользователя
        :param language_code: Языковая настройка
        """
        admin = Admin(
            id=admin_id,
            language_code=language_code,
            name=name
        )
        session.add(admin)
        await session.commit()
        return admin

    async def get_admin(self, session: AsyncSession,
                        admin_id: int) -> Admin | None:
        """
        Возвращает администратора по ID

        :param admin_id: Telegram ID администратора
        :return: None если не найден, иначе Admin
        """
        query = select(Admin).where(Admin.id == admin_id)
        admin: Admin | None = await session.scalar(query)
        return admin

    async def get_admins_bots(self, session: AsyncSession,
                              admin_id: int) -> list[Bot]:
        """
        Получает список ботов админа

        :param admin_id: Telegram ID админа
        :return: список ботов
        """
        query = select(Admin).options(
            selectinload(Admin.bots)
        ).where(Admin.id == admin_id)
        result: Result = await session.execute(query)
        admin: Admin | None = result.scalars().first()
        if admin is not None:
            return admin.bots
        return []

    async def assign_admin_label(self, session: AsyncSession,
                                 admin_id: int, label: str | None = None) -> str:
        """
        Присваивает администратору уникальный label.
        Если label не передан, то будет сгенерирован новый UUID4.

        :param admin_id: ID администратора
        :param label: опциональный label, если не передан, будет сгенерирован
        :return: присвоенный label
        """
        # Если label не передан, генерируем новый UUID4
        if label is None:
            label = str(uuid.uuid4())
        
        # Обновляем label у администратора
        query = (
            update(Admin)
            .where(Admin.id == admin_id)
            .values({"label": label})
            .returning(Admin.label)
        )

        result = await session.execute(query)
        await session.commit()

        # Возвращаем присвоенный label
        return result.scalar()
    
