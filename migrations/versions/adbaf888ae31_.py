"""Change archived bool to timestamp and add merged time

Revision ID: adbaf888ae31
Revises: 0856e735a1a4
Create Date: 2020-01-19 14:19:24.085140
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'adbaf888ae31'
down_revision = '0856e735a1a4'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('draft_mod', sa.Column('archived_time', sa.DateTime(timezone=True), nullable=True))
    op.add_column('draft_mod', sa.Column('merged_time', sa.DateTime(timezone=True), nullable=True))
    op.execute("UPDATE draft_mod "
               "SET archived_time = (now() at time zone 'utc'), "
               "merged_time = (now() at time zone 'utc') "
               "WHERE archived = true ")
    op.execute("UPDATE draft_mod "
               "SET archived_time = null, "
               "merged_time = null "
               "WHERE archived = false ")
    op.drop_column('draft_mod', 'archived')


def downgrade():
    op.add_column('draft_mod', sa.Column('archived', sa.BOOLEAN(), autoincrement=False,
        nullable=True))
    op.execute("UPDATE draft_mod "
               "SET archived = false "
               "WHERE archived_time IS NULL")
    op.execute("UPDATE draft_mod "
               "SET archived = true "
               "WHERE archived_time IS NOT NULL")
    op.alter_column('draft_mod', 'archived', nullable=False)

    op.drop_column('draft_mod', 'merged_time')
    op.drop_column('draft_mod', 'archived_time')

