"""Add user settings table

Revision ID: e529f7080cbd
Revises: 0b9f0e3e7d95
Create Date: 2020-02-21 21:55:54.664513
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e529f7080cbd'
down_revision = '0b9f0e3e7d95'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('user_setting',
        sa.Column('key', sa.String(length=40), nullable=False),
        sa.Column('value', sa.JSON(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('key', 'user_id')
    )

def downgrade():
    op.drop_table('user_setting')

