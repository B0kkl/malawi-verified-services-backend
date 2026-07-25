"""create api applications table

Revision ID: f2d2aab5d056
Revises: 1874a79b27c2
Create Date: 2026-07-25 13:19:46.712463
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f2d2aab5d056"
down_revision: Union[str, Sequence[str], None] = "1874a79b27c2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "api_applications",
        sa.Column(
            "company_name",
            sa.String(length=200),
            nullable=False,
        ),
        sa.Column(
            "contact_name",
            sa.String(length=150),
            nullable=False,
        ),
        sa.Column(
            "email",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "website",
            sa.String(length=500),
            nullable=True,
        ),
        sa.Column(
            "purpose",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "api_key_prefix",
            sa.String(length=32),
            nullable=False,
        ),
        sa.Column(
            "api_key_hash",
            sa.String(length=64),
            nullable=False,
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default="1",
            nullable=False,
        ),
        sa.Column(
            "request_count",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),
        sa.Column(
            "last_used_at",
            sa.DateTime(timezone=True),
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
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_api_applications_api_key_hash"),
        "api_applications",
        ["api_key_hash"],
        unique=True,
    )

    op.create_index(
        op.f("ix_api_applications_api_key_prefix"),
        "api_applications",
        ["api_key_prefix"],
        unique=False,
    )

    op.create_index(
        op.f("ix_api_applications_company_name"),
        "api_applications",
        ["company_name"],
        unique=False,
    )

    op.create_index(
        op.f("ix_api_applications_email"),
        "api_applications",
        ["email"],
        unique=False,
    )

    op.create_index(
        op.f("ix_api_applications_id"),
        "api_applications",
        ["id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_api_applications_id"),
        table_name="api_applications",
    )

    op.drop_index(
        op.f("ix_api_applications_email"),
        table_name="api_applications",
    )

    op.drop_index(
        op.f("ix_api_applications_company_name"),
        table_name="api_applications",
    )

    op.drop_index(
        op.f("ix_api_applications_api_key_prefix"),
        table_name="api_applications",
    )

    op.drop_index(
        op.f("ix_api_applications_api_key_hash"),
        table_name="api_applications",
    )

    op.drop_table("api_applications")