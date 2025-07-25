"""Sender ids are unique again

Revision ID: 0fa7871c5bcd
Revises: 2d5b0ce2c3ef
Create Date: 2024-08-30 12:01:15.994242

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0fa7871c5bcd'
down_revision: Union[str, None] = '2d5b0ce2c3ef'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('ad_message',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('html_text', sa.Text(), nullable=False),
    sa.Column('photo_link', sa.String(length=255), nullable=True),
    sa.Column('message_data', sa.JSON(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('ad_message_views',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('view_date', sa.Date(), nullable=False),
    sa.Column('view_count', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('admin',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('language_code', sa.String(length=2), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('is_active', sa.Boolean(), server_default='True', nullable=False),
    sa.Column('label', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('invite_codes',
    sa.Column('code', sa.String(length=255), nullable=False),
    sa.Column('bot_id', sa.BigInteger(), nullable=False),
    sa.Column('is_active', sa.Boolean(), server_default='True', nullable=False),
    sa.PrimaryKeyConstraint('code')
    )
    op.create_table('mailing_message',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('html_text', sa.Text(), nullable=False),
    sa.Column('inline_text', sa.String(length=255), nullable=False),
    sa.Column('inline_url', sa.String(length=255), nullable=False),
    sa.Column('message_data', sa.JSON(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('bot',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('url', sa.String(length=255), nullable=False),
    sa.Column('language_code', sa.String(length=2), nullable=False),
    sa.Column('banlist', sa.ARRAY(sa.BigInteger()), nullable=True),
    sa.Column('sign_messages', sa.Boolean(), server_default='True', nullable=False),
    sa.Column('post_formatting', sa.String(length=255), nullable=True),
    sa.Column('token', sa.String(length=255), nullable=False),
    sa.Column('is_active', sa.Boolean(), server_default='True', nullable=False),
    sa.Column('is_premium', sa.Boolean(), server_default='False', nullable=False),
    sa.Column('creator_id', sa.BigInteger(), nullable=False),
    sa.ForeignKeyConstraint(['creator_id'], ['admin.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('token')
    )
    op.create_table('subscription',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('admin_id', sa.BigInteger(), nullable=False),
    sa.Column('start_date', sa.DateTime(timezone=True), nullable=False),
    sa.Column('end_date', sa.DateTime(timezone=True), nullable=False),
    sa.Column('plan', sa.String(length=255), nullable=False),
    sa.ForeignKeyConstraint(['admin_id'], ['admin.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('admin_bot_association',
    sa.Column('admin_id', sa.BigInteger(), nullable=False),
    sa.Column('bot_id', sa.BigInteger(), nullable=False),
    sa.ForeignKeyConstraint(['admin_id'], ['admin.id'], ),
    sa.ForeignKeyConstraint(['bot_id'], ['bot.id'], ),
    sa.PrimaryKeyConstraint('admin_id', 'bot_id')
    )
    op.create_table('channels',
    sa.Column('primary_key', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('bot_id', sa.BigInteger(), nullable=True),
    sa.ForeignKeyConstraint(['bot_id'], ['bot.id'], ),
    sa.PrimaryKeyConstraint('primary_key')
    )
    op.create_table('sender',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('first_name', sa.String(length=255), nullable=False),
    sa.Column('bot_id', sa.BigInteger(), nullable=True),
    sa.Column('is_active', sa.Boolean(), server_default='True', nullable=False),
    sa.ForeignKeyConstraint(['bot_id'], ['bot.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('suggested_message',
    sa.Column('primary_key', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('chat_id', sa.BigInteger(), nullable=False),
    sa.Column('media_group_id', sa.String(length=255), nullable=False),
    sa.Column('group_id', sa.String(length=255), nullable=False),
    sa.Column('sender_id', sa.BigInteger(), nullable=False),
    sa.Column('bot_id', sa.BigInteger(), nullable=True),
    sa.Column('html_text', sa.Text(), nullable=False),
    sa.Column('message_data', sa.JSON(), nullable=False),
    sa.ForeignKeyConstraint(['bot_id'], ['bot.id'], ),
    sa.ForeignKeyConstraint(['sender_id'], ['sender.id'], ),
    sa.PrimaryKeyConstraint('primary_key')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('suggested_message')
    op.drop_table('sender')
    op.drop_table('channels')
    op.drop_table('admin_bot_association')
    op.drop_table('subscription')
    op.drop_table('bot')
    op.drop_table('mailing_message')
    op.drop_table('invite_codes')
    op.drop_table('admin')
    op.drop_table('ad_message_views')
    op.drop_table('ad_message')
    # ### end Alembic commands ###
