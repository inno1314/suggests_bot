import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import date
from typing import Any

from .base_class import BaseDBApi
from .model import AdMessageViews, AdMessage, MailingMessage

logger = logging.getLogger(__name__)

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
            logger.info("Added today's message view in DB")
        else:
            views = message_view.view_count
            stmt = (
                update(AdMessageViews)
                .where(AdMessageViews.id == message_view.id)
                .values(view_count=message_view.view_count + 1)
            )
            await session.execute(stmt)
            logger.info(f"Incremented message_views {views} -> {views + 1}")

        await session.commit()

    async def add_mailing_message(self, session: AsyncSession,
                              data: Any, html_text: str):
        message = MailingMessage(
            html_text = html_text,
            inline_text = "",
            inline_url = "",
            message_data = data
        )
        session.add(message)
        logger.info("Added new mailing message in DB")
        await session.commit()

    async def get_ad_message(self, session: AsyncSession) -> AdMessage | None:
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
        logger.info("Edited mailing message in DB")
        await session.commit()

