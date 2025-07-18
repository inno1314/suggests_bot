"""Added name field for admins

Revision ID: 6b8ecbb3115b
Revises: 39ac3d720233
Create Date: 2024-06-24 21:28:08.624725

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6b8ecbb3115b'
down_revision: Union[str, None] = '39ac3d720233'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('admin', sa.Column('name', sa.String(length=255), nullable=True))
    op.drop_column('admin', 'is_premium')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('admin', sa.Column('is_premium', sa.BOOLEAN(), server_default=sa.text('true'), autoincrement=False, nullable=False))
    op.drop_column('admin', 'name')
    # ### end Alembic commands ###
