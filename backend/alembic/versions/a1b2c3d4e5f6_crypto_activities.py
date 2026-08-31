"""Alembic migration: crypto_activities audit table

Revision ID: a1b2c3d4e5f6
Revises: ecbbbfc17490
Create Date: 2026-08-31 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "ecbbbfc17490"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "crypto_activities",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("file_id", sa.UUID(), nullable=True),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("original_name", sa.String(), nullable=True),
        sa.Column("file_size_bytes", sa.BigInteger(), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["file_id"], ["files.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_crypto_activities_id"), "crypto_activities", ["id"], unique=False)
    op.create_index(op.f("ix_crypto_activities_user_id"), "crypto_activities", ["user_id"], unique=False)
    op.create_index(op.f("ix_crypto_activities_file_id"), "crypto_activities", ["file_id"], unique=False)
    op.create_index(op.f("ix_crypto_activities_created_at"), "crypto_activities", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_crypto_activities_created_at"), table_name="crypto_activities")
    op.drop_index(op.f("ix_crypto_activities_file_id"), table_name="crypto_activities")
    op.drop_index(op.f("ix_crypto_activities_user_id"), table_name="crypto_activities")
    op.drop_index(op.f("ix_crypto_activities_id"), table_name="crypto_activities")
    op.drop_table("crypto_activities")
