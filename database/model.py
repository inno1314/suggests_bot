from datetime import datetime, date, timezone
from sqlalchemy import (
    Table,
    Column,
    Boolean,
    BigInteger,
    String,
    ARRAY,
    ForeignKey,
    DateTime,
    Date,
    JSON,
    Text,
    Integer,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

admin_bot_association = Table(
    "admin_bot_association",
    Base.metadata,
    Column("admin_id", BigInteger, ForeignKey("admin.id"), primary_key=True),
    Column("bot_id", BigInteger, ForeignKey("bot.id"), primary_key=True),
)


class Bot(Base):
    __tablename__ = "bot"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    url: Mapped[str] = mapped_column(String(255))
    language_code: Mapped[str] = mapped_column(String(2))
    banlist: Mapped[list[int]] = mapped_column(
        ARRAY(BigInteger), default=list, nullable=True
    )
    sign_messages: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default="True"
    )
    post_formatting: Mapped[str] = mapped_column(Text, nullable=True)
    start_message: Mapped[str] = mapped_column(Text, nullable=True)
    answer_message: Mapped[str] = mapped_column(Text, nullable=True)
    token: Mapped[str] = mapped_column(String(255), unique=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default="True"
    )
    is_premium: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="False"
    )

    channels: Mapped["Channels"] = relationship(back_populates="bot")
    creator_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("admin.id"))
    admins: Mapped[list["Admin"]] = relationship(
        "Admin", secondary=admin_bot_association, back_populates="bots"
    )
    suggesters: Mapped[list["Sender"]] = relationship(back_populates="bot")
    messages: Mapped["SuggestedMessage"] = relationship(back_populates="bot")


class Admin(Base):
    __tablename__ = "admin"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    language_code: Mapped[str] = mapped_column(String(2))
    name: Mapped[str] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default="True"
    )
    label: Mapped[str] = mapped_column(String(255), nullable=True, default="None")

    bots: Mapped[list["Bot"]] = relationship(
        "Bot", secondary=admin_bot_association, back_populates="admins"
    )
    subscriptions: Mapped[list["Subscription"]] = relationship(
        "Subscription", back_populates="admin"
    )


class Subscription(Base):
    __tablename__ = "subscription"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    admin_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("admin.id"))
    start_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now(timezone.utc)
    )
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    plan: Mapped[str] = mapped_column(String(255))

    admin: Mapped["Admin"] = relationship("Admin", back_populates="subscriptions")


class Payments(Base):
    __tablename__ = "payments"

    payment_id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    amount: Mapped[float] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="created")
    service: Mapped[str] = mapped_column(String, nullable=False)
    date: Mapped[str] = mapped_column(String, nullable=False)


class Sender(Base):
    __tablename__ = "sender"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(255))
    bot_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("bot.id", ondelete="SET NULL"), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default="True"
    )
    bot: Mapped["Bot"] = relationship(back_populates="suggesters")
    suggests: Mapped[list["SuggestedMessage"]] = relationship(back_populates="sender")


class Channels(Base):
    __tablename__ = "channels"

    primary_key: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    id: Mapped[int] = mapped_column(BigInteger, unique=False)
    name: Mapped[str] = mapped_column(String(255))
    bot_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("bot.id"), nullable=True)

    bot: Mapped["Bot"] = relationship(back_populates="channels")


class SuggestedMessage(Base):
    __tablename__ = "suggested_message"

    primary_key: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    id: Mapped[int] = mapped_column(BigInteger)
    chat_id: Mapped[int] = mapped_column(BigInteger)
    media_group_id: Mapped[str] = mapped_column(String(255))
    group_id: Mapped[str] = mapped_column(String(255))
    sender_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("sender.id"))
    bot_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("bot.id"), nullable=True)
    html_text: Mapped[str] = mapped_column(Text)
    message_data: Mapped[dict] = mapped_column(JSON)

    bot: Mapped["Bot"] = relationship(back_populates="messages")
    sender: Mapped["Sender"] = relationship(back_populates="suggests")


class InviteCodes(Base):
    __tablename__ = "invite_codes"

    code: Mapped[str] = mapped_column(String(255), primary_key=True)
    bot_id: Mapped[int] = mapped_column(BigInteger)
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default="True"
    )


class AdMessageViews(Base):
    __tablename__ = "ad_message_views"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    view_date: Mapped[date] = mapped_column(Date, nullable=False)
    view_count: Mapped[int] = mapped_column(Integer, default=0)


class AdMessage(Base):
    __tablename__ = "ad_message"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    html_text: Mapped[str] = mapped_column(Text)
    photo_link: Mapped[str] = mapped_column(String(255), nullable=True)
    message_data: Mapped[dict] = mapped_column(JSON, nullable=True)


class MailingMessage(Base):
    __tablename__ = "mailing_message"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    html_text: Mapped[str] = mapped_column(Text)
    inline_text: Mapped[str] = mapped_column(String(255))
    inline_url: Mapped[str] = mapped_column(String(255))
    message_data: Mapped[dict] = mapped_column(JSON)
