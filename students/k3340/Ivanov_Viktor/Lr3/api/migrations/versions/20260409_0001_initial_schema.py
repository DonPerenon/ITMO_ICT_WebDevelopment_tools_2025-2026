"""initial schema

Revision ID: 20260409_0001
Revises:
Create Date: 2026-04-09 00:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260409_0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


transaction_type_enum = sa.Enum("income", "expense", name="transactiontype")
goal_status_enum = sa.Enum("active", "completed", "cancelled", name="goalstatus")


def upgrade() -> None:
    bind = op.get_bind()
    transaction_type_enum.create(bind, checkfirst=True)
    goal_status_enum.create(bind, checkfirst=True)

    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("username", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index(op.f("ix_user_username"), "user", ["username"], unique=True)
    op.create_index(op.f("ix_user_email"), "user", ["email"], unique=True)

    op.create_table(
        "category",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("tx_type", transaction_type_enum, nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False),
    )

    op.create_table(
        "tag",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False),
    )

    op.create_table(
        "goal",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("target_amount", sa.Float(), nullable=False),
        sa.Column("current_amount", sa.Float(), nullable=False, server_default="0"),
        sa.Column("deadline", sa.Date(), nullable=True),
        sa.Column("status", goal_status_enum, nullable=False, server_default="active"),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False),
    )

    op.create_table(
        "transaction",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("tx_type", transaction_type_enum, nullable=False),
        sa.Column("occurred_at", sa.DateTime(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("category.id"), nullable=True),
    )

    op.create_table(
        "budget",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("limit_amount", sa.Float(), nullable=False),
        sa.Column("spent_amount", sa.Float(), nullable=False, server_default="0"),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("category.id"), nullable=False),
        sa.UniqueConstraint(
            "user_id", "category_id", "period_start", "period_end", name="uq_budget_period"
        ),
    )

    op.create_table(
        "transactiontaglink",
        sa.Column("transaction_id", sa.Integer(), sa.ForeignKey("transaction.id"), primary_key=True),
        sa.Column("tag_id", sa.Integer(), sa.ForeignKey("tag.id"), primary_key=True),
        sa.Column("relevance", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("note", sa.String(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("transactiontaglink")
    op.drop_table("budget")
    op.drop_table("transaction")
    op.drop_table("goal")
    op.drop_table("tag")
    op.drop_table("category")
    op.drop_index(op.f("ix_user_email"), table_name="user")
    op.drop_index(op.f("ix_user_username"), table_name="user")
    op.drop_table("user")

    bind = op.get_bind()
    goal_status_enum.drop(bind, checkfirst=True)
    transaction_type_enum.drop(bind, checkfirst=True)
