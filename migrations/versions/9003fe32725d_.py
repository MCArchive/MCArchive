"""Add ready_time to drafts

Revision ID: 9003fe32725d
Revises: c31c7babde68
Create Date: 2020-01-21 11:09:52.777683
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9003fe32725d'
down_revision = 'c31c7babde68'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('draft_mod', sa.Column('ready_time', sa.DateTime(), nullable=True))

def downgrade():
    op.drop_column('draft_mod', 'ready_time')

