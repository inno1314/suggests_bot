"""Added json field for messages

Revision ID: 3c6fd367e6c1
Revises: 5470abc3be2d
Create Date: 2024-06-26 11:51:14.640096

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3c6fd367e6c1'
down_revision: Union[str, None] = '5470abc3be2d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('suggested_message', sa.Column('message_data', sa.JSON(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('suggested_message', 'message_data')
    # ### end Alembic commands ###
