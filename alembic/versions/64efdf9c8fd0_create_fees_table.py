"""create fees table

Revision ID: 64efdf9c8fd0
Revises: 2643792faefb
Create Date: 2026-07-20 17:24:43.097741
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "64efdf9c8fd0"
down_revision: Union[str, Sequence[str], None] = "2643792faefb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "fees",
        sa.Column(
            "service_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "name",
            sa.String(length=200),
            nullable=False,
        ),
        sa.Column(
            "amount",
            sa.Numeric(precision=12, scale=2),
            nullable=False,
        ),
        sa.Column(
            "currency",
            sa.String(length=10),
            nullable=False,
        ),
        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["service_id"],
            ["services.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_fees_id"),
        "fees",
        ["id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_fees_name"),
        "fees",
        ["name"],
        unique=False,
    )

    op.create_index(
        op.f("ix_fees_service_id"),
        "fees",
        ["service_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_fees_service_id"),
        table_name="fees",
    )

    op.drop_index(
        op.f("ix_fees_name"),
        table_name="fees",
    )

    op.drop_index(
        op.f("ix_fees_id"),
        table_name="fees",
    )

    op.drop_table("fees")
