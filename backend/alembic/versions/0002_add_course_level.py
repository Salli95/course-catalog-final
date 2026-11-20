"""add course level

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-06 14:12:38.334261

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0002'
down_revision: Union[str, Sequence[str], None] = '0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. allowing null
    op.add_column('courses', sa.Column('level', sa.Text(), nullable=True))

    # 2. filling rows
    op.execute("UPDATE courses SET level = CASE WHEN is_elective THEN 'beginner' ELSE 'intermediate' END")

    # 3. making not-null
    op.alter_column('courses', 'level', nullable=False)


def downgrade() -> None:
    op.drop_column('courses', 'level')
