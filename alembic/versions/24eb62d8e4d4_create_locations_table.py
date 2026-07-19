"""create locations table

Revision ID: 24eb62d8e4d4
Revises: b560f5bcda14
Create Date: 2026-07-20 00:17:00.184273
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "24eb62d8e4d4"
down_revision: Union[str, Sequence[str], None] = "b560f5bcda14"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "locations",
        sa.Column("agency_id", sa.Integer(), nullable=False),
        sa.Column("district", sa.String(length=100), nullable=False),
        sa.Column("physical_address", sa.Text(), nullable=False),
        sa.Column("postal_address", sa.String(length=255), nullable=True),
        sa.Column("phone_number", sa.String(length=50), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("is_head_office", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
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
            ["agency_id"],
            ["agencies.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_locations_agency_id"),
        "locations",
        ["agency_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_locations_district"),
        "locations",
        ["district"],
        unique=False,
    )

    op.create_index(
        op.f("ix_locations_email"),
        "locations",
        ["email"],
        unique=False,
    )

    op.create_index(
        op.f("ix_locations_id"),
        "locations",
        ["id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_locations_id"),
        table_name="locations",
    )

    op.drop_index(
        op.f("ix_locations_email"),
        table_name="locations",
    )

    op.drop_index(
        op.f("ix_locations_district"),
        table_name="locations",
    )

    op.drop_index(
        op.f("ix_locations_agency_id"),
        table_name="locations",
    )

    op.drop_table("locations")
