"""Add created and changed timestamp to mods

Revision ID: 0856e735a1a4
Revises: d21bef21f9b3
Create Date: 2020-01-18 18:56:38.641654

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utc

# revision identifiers, used by Alembic.
revision = '0856e735a1a4'
down_revision = 'd21bef21f9b3'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('draft_mod', sa.Column('time_changed', sqlalchemy_utc.UtcDateTime(timezone=True), nullable=True))
    op.add_column('draft_mod', sa.Column('time_created', sqlalchemy_utc.UtcDateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False))
    op.add_column('log_mod', sa.Column('time_changed', sqlalchemy_utc.UtcDateTime(timezone=True), nullable=True))
    op.add_column('log_mod', sa.Column('time_created', sqlalchemy_utc.UtcDateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False))
    op.add_column('mod', sa.Column('time_changed', sqlalchemy_utc.UtcDateTime(timezone=True), nullable=True))
    op.add_column('mod', sa.Column('time_created', sqlalchemy_utc.UtcDateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False))


def downgrade():
    op.drop_column('mod', 'time_created')
    op.drop_column('mod', 'time_changed')
    op.drop_column('log_mod', 'time_created')
    op.drop_column('log_mod', 'time_changed')
    op.drop_column('draft_mod', 'time_created')
    op.drop_column('draft_mod', 'time_changed')

