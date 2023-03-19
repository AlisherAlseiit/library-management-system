"""create tables

Revision ID: 7181a08b1331
Revises: 
Create Date: 2023-03-15 22:16:04.734689

"""
from alembic import op
import sqlalchemy as sa
from app import utils

# revision identifiers, used by Alembic.
revision = '7181a08b1331'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('books',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('genre', sa.String(), nullable=False),
    sa.Column('available', sa.Boolean(), server_default='TRUE', nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    roles_table = op.create_table('roles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    users_table = op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(), nullable=False),
    sa.Column('password', sa.String(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    user_roles_table = op.create_table('user_roles',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('role_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id', 'role_id')
    )

    op.bulk_insert(roles_table,
        [
            {"name": "admin"},
            {"name": "user"}
        ]
    )

    op.bulk_insert(users_table,
        [
            {"username": "admin", "password": f"{utils.hash('admin')}"},
            {"username": "alish", "password": f"{utils.hash('123')}"}
        ]
    )

    op.bulk_insert(user_roles_table,
        [
            {"user_id": 1, "role_id": 1},
            {"user_id": 2, "role_id": 2}
        ]          
    )
    
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_roles')
    op.drop_table('users')
    op.drop_table('roles')
    op.drop_table('books')
    # ### end Alembic commands ###
