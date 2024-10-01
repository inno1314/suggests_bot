"""Added new primary key for channels

Revision ID: 6a3eb65e7a6a
Revises: 4e79998d9f80
Create Date: 2024-08-22 18:55:13.106109

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6a3eb65e7a6a'
down_revision: Union[str, None] = '4e79998d9f80'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Шаг 1: Создаем новую последовательность
    # op.execute("CREATE SEQUENCE channels_primary_key_seq")
    # Шаг 2: Добавляем новый столбец без NOT NULL
    op.add_column('channels', sa.Column('primary_key', sa.BigInteger(), nullable=True))
    # Шаг 3: Присваиваем значения столбцу primary_key, используя созданную последовательность
    op.execute("UPDATE channels SET primary_key = nextval('channels_primary_key_seq')")
    # Шаг 4: Устанавливаем ограничение NOT NULL и создаем PRIMARY KEY
    op.alter_column('channels', 'primary_key', nullable=False)
    op.create_primary_key('pk_channels', 'channels', ['primary_key'])


def downgrade() -> None:
    op.drop_constraint('pk_channels', 'channels', type_='primary')
    op.drop_column('channels', 'primary_key')

    # Удаляем последовательность
    op.execute("DROP SEQUENCE channels_primary_key_seq")
