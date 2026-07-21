"""create documents table

Revision ID: 1874a79b27c2
Revises: 41fd4014b50a
Create Date: 2026-07-20 18:33:37.631123
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "1874a79b27c2"
down_revision: Union[str, Sequence[str], None] = "41fd4014b50a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "documents",
        sa.Column(
            "service_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "title",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "document_type",
            sa.String(length=50),
            nullable=True,
        ),
        sa.Column(
            "file_url",
            sa.String(length=1000),
            nullable=False,
        ),
        sa.Column(
            "is_downloadable",
            sa.Boolean(),
            server_default="1",
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
        op.f("ix_documents_id"),
        "documents",
        ["id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_documents_service_id"),
        "documents",
        ["service_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_documents_title"),
        "documents",
        ["title"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_documents_title"),
        table_name="documents",
    )

    op.drop_index(
        op.f("ix_documents_service_id"),
        table_name="documents",
    )

    op.drop_index(
        op.f("ix_documents_id"),
        table_name="documents",
    )

    op.drop_table("documents")
