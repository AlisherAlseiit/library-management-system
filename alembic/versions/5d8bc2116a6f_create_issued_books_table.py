"""create issued books table

Revision ID: 5d8bc2116a6f
Revises: 7181a08b1331
Create Date: 2023-03-16 19:25:09.968360

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5d8bc2116a6f'
down_revision = '7181a08b1331'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('borrowed_books',
    sa.Column("book_id", sa.Integer(), nullable=False),
    sa.Column("user_id", sa.Integer(), nullable=False),
    sa.Column('borrowed_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('returned_at', sa.TIMESTAMP(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    sa.ForeignKeyConstraint(["book_id"], ["books.id"], ondelete="CASCADE"),
    sa.PrimaryKeyConstraint("user_id", "book_id", "borrowed_at")
    )


def downgrade() -> None:
    op.drop_table("borrowed_books")
