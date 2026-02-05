"""add display_name to users

Revision ID: rev0002
Revises: rev0001
Create Date: 2026-02-05
"""

import sqlalchemy as sa
from alembic import op

revision = "rev0002"
down_revision = "rev0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("display_name", sa.String(255), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "display_name")
