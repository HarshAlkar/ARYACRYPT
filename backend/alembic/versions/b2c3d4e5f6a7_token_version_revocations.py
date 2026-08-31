"""Add token_version and refresh_token_revocations

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-08-31 17:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("token_version", sa.Integer(), server_default="0", nullable=False),
    )
    op.create_table(
        "refresh_token_revocations",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash"),
    )
    op.create_index("ix_refresh_token_revocations_token_hash", "refresh_token_revocations", ["token_hash"])
    op.create_index("ix_refresh_token_revocations_user_id", "refresh_token_revocations", ["user_id"])
    op.create_index("ix_refresh_token_revocations_expires_at", "refresh_token_revocations", ["expires_at"])


def downgrade() -> None:
    op.drop_index("ix_refresh_token_revocations_expires_at", table_name="refresh_token_revocations")
    op.drop_index("ix_refresh_token_revocations_user_id", table_name="refresh_token_revocations")
    op.drop_index("ix_refresh_token_revocations_token_hash", table_name="refresh_token_revocations")
    op.drop_table("refresh_token_revocations")
    op.drop_column("users", "token_version")
