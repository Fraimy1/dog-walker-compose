"""initial schema

Revision ID: rev0001
Revises:
Create Date: 2026-02-05
"""

import sqlalchemy as sa
from alembic import op

revision = "rev0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("telegram_id", sa.BigInteger(), unique=True, index=True, nullable=False),
        sa.Column("username", sa.String(255), nullable=True),
        sa.Column("language", sa.String(2), server_default="ru", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("1"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "walks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("walked_at", sa.DateTime(), nullable=False),
        sa.Column("didnt_poop", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        sa.Column("long_walk", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        sa.Column("is_finalized", sa.Boolean(), server_default=sa.text("0"), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("walks")
    op.drop_table("users")
