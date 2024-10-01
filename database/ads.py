from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import date

from utils import logger
from .base_class import BaseDBApi
from .model import AdMessageViews, AdMessage, MailingMessage

class AdsDatabaseApi(BaseDBApi):
    async def count_views(self, session: AsyncSession):
        today = date.today()
        query = select(AdMessageViews).where(AdMessageViews.view_date == today)
        result = await session.execute(query)
        message_view = result.scalar_one_or_none()
    
        if message_view is None:
            message_view = AdMessageViews(
                view_date = today,
                view_count = 1
            )
            session.add(message_view)
            logger.info("added message views for today")
        else:
            stmt = (
                update(AdMessageViews)
                .where(AdMessageViews.id == message_view.id)
                .values(view_count=message_view.view_count + 1)
            )
            logger.info(f"message_views are {message_view.view_count + 1} now")
            await session.execute(stmt)

        await session.commit()

    async def add_mailing_message(self, session: AsyncSession,
                              data: any, html_text: str):
        message = MailingMessage(
            html_text = html_text,
            inline_text = "",
            inline_url = "",
            message_data = data
        )
        session.add(message)
        await session.commit()

    async def get_ad_message(self, session: AsyncSession) -> AdMessage or None:
        query = select(AdMessage).where(AdMessage.id == 1)
        result = await session.execute(query)
        ad_message = result.scalar_one_or_none()
        return ad_message

    async def edit_ad_message(self, session: AsyncSession,
                              html_text: str, link: str | None = None):
        query = (
            update(AdMessage)
            .where(AdMessage.id == 1)
            .values(html_text=html_text, photo_link=link)
        )
        await session.execute(query)
        await session.commit()

