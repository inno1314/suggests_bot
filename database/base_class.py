from sqlalchemy.ext.asyncio import AsyncSession

class BaseDBApi:
    def __init__(self, session: AsyncSession):
        self.session = session

