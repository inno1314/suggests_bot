"""Added admin -> bot associations

Revision ID: d6af391c775e
Revises: da9c8e75bc60
Create Date: 2024-06-20 16:09:40.424122

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd6af391c775e'
down_revision: Union[str, None] = 'da9c8e75bc60'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('admin_bot_association',
    sa.Column('admin_id', sa.BigInteger(), nullable=False),
    sa.Column('bot_id', sa.BigInteger(), nullable=False),
    sa.ForeignKeyConstraint(['admin_id'], ['admin.id'], ),
    sa.ForeignKeyConstraint(['bot_id'], ['bot.id'], ),
    sa.PrimaryKeyConstraint('admin_id', 'bot_id')
    )
    op.drop_column('sender', 'is_banned')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('sender', sa.Column('is_banned', sa.BOOLEAN(), server_default=sa.text('false'), autoincrement=False, nullable=False))
    op.drop_table('admin_bot_association')
    # ### end Alembic commands ###
