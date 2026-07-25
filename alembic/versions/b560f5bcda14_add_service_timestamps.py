"""add service timestamps

Revision ID: b560f5bcda14
Revises: a1c4e7f9b203
Create Date: 2026-07-19 21:12:48.760737
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b560f5bcda14"
down_revision: Union[str, Sequence[str], None] = "a1c4e7f9b203"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "services",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    op.add_column(
        "services",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    op.execute(
        """
        UPDATE services
        SET created_at = CURRENT_TIMESTAMP,
            updated_at = CURRENT_TIMESTAMP
        WHERE created_at IS NULL
           OR updated_at IS NULL
        """
    )


def downgrade() -> None:
    op.drop_column("services", "updated_at")
    op.drop_column("services", "created_at")

