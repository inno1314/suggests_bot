"""Sender ids are not more unique

Revision ID: 2d5b0ce2c3ef
Revises: 316e6976a9d7
Create Date: 2024-08-24 16:34:35.207364

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2d5b0ce2c3ef'
down_revision: Union[str, None] = '316e6976a9d7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute('ALTER TABLE sender DROP CONSTRAINT IF EXISTS sender_pkey CASCADE') 
    # Шаг 1: Создаем новую последовательность
    op.execute("CREATE SEQUENCE sender_primary_key_seq")
    # Шаг 2: Добавляем новый столбец без NOT NULL
    op.add_column('sender', sa.Column('primary_key', sa.Integer(), nullable=True))
    # Шаг 3: Присваиваем значения столбцу primary_key, используя созданную последовательность
    op.execute("UPDATE sender SET primary_key = nextval('sender_primary_key_seq')")
    # Шаг 4: Устанавливаем ограничение NOT NULL и создаем PRIMARY KEY
    op.alter_column('sender', 'primary_key', nullable=False)
    op.create_primary_key('pk_sender', 'sender', ['primary_key'])

def downgrade():
    # Восстанавливаем изменения при откате
    op.drop_constraint('pk_sender', 'sender', type_='primary')
    op.drop_column('sender', 'primary_key')
    op.create_primary_key('sender_pkey', 'sender', ['id'])
    # Удаляем последовательность
    op.execute("DROP SEQUENCE sender_primary_key_seq")

