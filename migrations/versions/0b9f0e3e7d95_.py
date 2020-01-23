"""Add redist flag to mod table

Revision ID: 0b9f0e3e7d95
Revises: 9003fe32725d
Create Date: 2020-01-23 14:16:00.267540
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0b9f0e3e7d95'
down_revision = '9003fe32725d'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('mod', sa.Column('redist', sa.Boolean(), nullable=False, server_default='true'))

def downgrade():
    op.drop_column('mod', 'redist')

