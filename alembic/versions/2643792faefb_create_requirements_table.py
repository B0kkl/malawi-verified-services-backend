"""create requirements table

Revision ID: 2643792faefb
Revises: 24eb62d8e4d4
Create Date: 2026-07-20 01:01:39.342550
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "2643792faefb"
down_revision: Union[str, Sequence[str], None] = "24eb62d8e4d4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "requirements",
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
            "description",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "is_mandatory",
            sa.Boolean(),
            nullable=False,
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
        op.f("ix_requirements_id"),
        "requirements",
        ["id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_requirements_name"),
        "requirements",
        ["name"],
        unique=False,
    )

    op.create_index(
        op.f("ix_requirements_service_id"),
        "requirements",
        ["service_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_requirements_service_id"),
        table_name="requirements",
    )

    op.drop_index(
        op.f("ix_requirements_name"),
        table_name="requirements",
    )

    op.drop_index(
        op.f("ix_requirements_id"),
        table_name="requirements",
    )

    op.drop_table("requirements")
