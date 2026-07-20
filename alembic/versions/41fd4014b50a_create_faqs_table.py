"""create faqs table

Revision ID: 41fd4014b50a
Revises: 64efdf9c8fd0
Create Date: 2026-07-20 18:01:50.425521
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "41fd4014b50a"
down_revision: Union[str, Sequence[str], None] = "64efdf9c8fd0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "faqs",
        sa.Column(
            "service_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "question",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "answer",
            sa.Text(),
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
        op.f("ix_faqs_id"),
        "faqs",
        ["id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_faqs_service_id"),
        "faqs",
        ["service_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_faqs_service_id"),
        table_name="faqs",
    )

    op.drop_index(
        op.f("ix_faqs_id"),
        table_name="faqs",
    )

    op.drop_table("faqs")
