"""Remove `time_created` and `time_changed` from tables other than drafts

Revision ID: 87d8581aafb7
Revises: adbaf888ae31
Create Date: 2020-01-19 17:45:16.033546
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '87d8581aafb7'
down_revision = 'adbaf888ae31'
branch_labels = None
depends_on = None

def upgrade():
    op.drop_column('log_mod', 'time_created')
    op.drop_column('log_mod', 'time_changed')
    op.drop_column('mod', 'time_created')
    op.drop_column('mod', 'time_changed')
    op.execute('ALTER TABLE draft_mod ALTER COLUMN time_created TYPE timestamp without time zone')
    op.execute('ALTER TABLE draft_mod ALTER COLUMN time_changed TYPE timestamp without time zone')
    op.execute('ALTER TABLE draft_mod ALTER COLUMN merged_time TYPE timestamp without time zone')
    op.execute('ALTER TABLE draft_mod ALTER COLUMN archived_time TYPE timestamp without time zone')

def downgrade():
    op.add_column('mod', sa.Column('time_changed',
        postgresql.TIMESTAMP(timezone=True), autoincrement=False,
        nullable=True))
    op.add_column('mod', sa.Column('time_created',
        postgresql.TIMESTAMP(timezone=True),
        server_default=sa.text('CURRENT_TIMESTAMP'), autoincrement=False,
        nullable=False))
    op.add_column('log_mod', sa.Column('time_changed',
        postgresql.TIMESTAMP(timezone=True), autoincrement=False,
        nullable=True))
    op.add_column('log_mod', sa.Column('time_created',
        postgresql.TIMESTAMP(timezone=True),
        server_default=sa.text('CURRENT_TIMESTAMP'), autoincrement=False,
        nullable=False))
    op.execute('ALTER TABLE draft_mod ALTER COLUMN time_created TYPE timestamp with time zone')
    op.execute('ALTER TABLE draft_mod ALTER COLUMN time_changed TYPE timestamp with time zone')
    op.execute('ALTER TABLE draft_mod ALTER COLUMN merged_time TYPE timestamp with time zone')
    op.execute('ALTER TABLE draft_mod ALTER COLUMN archived_time TYPE timestamp with time zone')

