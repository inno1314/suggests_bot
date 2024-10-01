from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.engine import Result

from .base_class import BaseDBApi
from .model import InviteCodes
from utils import generate_id

class InviteCodesDatabaseApi(BaseDBApi):
    async def add_code(self, session: AsyncSession, bot_id: int) -> str:
        """
        Добавляет пригласительный код в БД
        :param bot_id: Telegram ID бота, для которого будет назначен новый администратор
        :return: Уникальный код для формирования ссылки
        """
        code = generate_id()

        db_code = InviteCodes(
            code=code,
            bot_id=bot_id
        )
        session.add(db_code)
        await session.commit()

        return code

    async def use_code(self, session: AsyncSession, code: str) -> int | None:
        """
        Возвращает Telegram ID бота, который привязан к коду
        :param code: Пригласительный код
        :return: bot.id, если кода нет в БД то None
        """
        query = select(InviteCodes).where(InviteCodes.code == code)
        db_code: InviteCodes | None = await session.scalar(query)

        if db_code is not None:
            bot_id = db_code.bot_id
            await session.delete(db_code)
            await session.flush()
            await session.commit()
            return bot_id

        return None

