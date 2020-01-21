"""Make URL string limits large

Revision ID: c31c7babde68
Revises: 5ee28b6c78b2
Create Date: 2020-01-20 21:19:30.323891

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c31c7babde68'
down_revision = '5ee28b6c78b2'
branch_labels = None
depends_on = None


def upgrade():
	op.alter_column('mod', 'website', type_=sa.String(2048))
	op.alter_column('log_mod', 'website', type_=sa.String(2048))
	op.alter_column('draft_mod', 'website', type_=sa.String(2048))

	op.alter_column('mod_version', 'url', type_=sa.String(2048))
	op.alter_column('log_mod_version', 'url', type_=sa.String(2048))
	op.alter_column('draft_mod_version', 'url', type_=sa.String(2048))

	for table in ['mod_file', 'log_mod_file', 'draft_mod_file']:
		op.alter_column(table, 'page_url', type_=sa.String(2048))
		op.alter_column(table, 'redirect_url', type_=sa.String(2048))
		op.alter_column(table, 'direct_url', type_=sa.String(2048))
	
	op.alter_column('author', 'website', type_=sa.String(2048))

def downgrade():
	op.alter_column('mod', 'website', type_=sa.String(120))
	op.alter_column('log_mod', 'website', type_=sa.String(120))
	op.alter_column('draft_mod', 'website', type_=sa.String(120))

	op.alter_column('mod_version', 'url', type_=sa.String(120))
	op.alter_column('log_mod_version', 'url', type_=sa.String(120))
	op.alter_column('draft_mod_version', 'url', type_=sa.String(120))

	for table in ['mod_file', 'log_mod_file', 'draft_mod_file']:
		op.alter_column(table, 'page_url', type_=sa.String(500))
		op.alter_column(table, 'redirect_url', type_=sa.String(500))
		op.alter_column(table, 'direct_url', type_=sa.String(500))
	
	op.alter_column('author', 'website', type_=sa.String(500))


