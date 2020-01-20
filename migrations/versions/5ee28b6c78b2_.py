"""Add approved_by field to drafts

Revision ID: 5ee28b6c78b2
Revises: 87d8581aafb7
Create Date: 2020-01-19 22:00:53.208404
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5ee28b6c78b2'
down_revision = '87d8581aafb7'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('log_mod', sa.Column('approved_by_id', sa.Integer(), nullable=True))
    op.create_foreign_key('log_mod_approved_by_id_fkey', 'log_mod', 'user',
            ['approved_by_id'], ['id'])


def downgrade():
    op.drop_constraint('log_mod_approved_by_id_fkey', 'log_mod', type_='foreignkey')
    op.drop_column('log_mod', 'approved_by_id')

