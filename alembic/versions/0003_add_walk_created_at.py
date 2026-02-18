"""add created_at to walks

Revision ID: rev0003
Revises: rev0002
Create Date: 2026-02-18
"""

import sqlalchemy as sa
from alembic import op

revision = "rev0003"
down_revision = "rev0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "walks",
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )


def downgrade() -> None:
    op.drop_column("walks", "created_at")
