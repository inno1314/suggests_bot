from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine 

from .model import Base

from .bot import BotDatabaseApi
from .admin import AdminDatabaseApi
from .subscription import SubscriptionDatabaseApi
from .payments import PaymentsDatabaseAPI
from .sender import SenderDatabaseApi
from .channel import ChannelDatabaseApi
from .message import MessageDatabaseApi
from .invites import InviteCodesDatabaseApi
from .ads import AdsDatabaseApi

class DataBaseApi:
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.engine = create_async_engine(self.db_url, echo=False)
        self.session_maker = async_sessionmaker(bind=self.engine, class_=AsyncSession, expire_on_commit=False)
        self.session = self.session_maker()

        self.bot_api = BotDatabaseApi(self.session)
        self.admin_api = AdminDatabaseApi(self.session)
        self.subscription_api = SubscriptionDatabaseApi(self.session)
        self.payments_api = PaymentsDatabaseAPI(self.session)
        self.sender_api = SenderDatabaseApi(self.session)
        self.channel_api = ChannelDatabaseApi(self.session)
        self.message_api = MessageDatabaseApi(self.session)
        self.codes_api = InviteCodesDatabaseApi(self.session)
        self.ads_api = AdsDatabaseApi(self.session)

    async def create_db(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_db(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

