"""Initial Revision

Revision ID: d21bef21f9b3
Revises:
Create Date: 2020-01-13 16:39:51.836656

"""
from alembic import op
import sqlalchemy as sa
import mcarch


# revision identifiers, used by Alembic.
revision = 'd21bef21f9b3'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('author',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=80), nullable=False),
    sa.Column('desc', sa.Text(), nullable=False),
    sa.Column('website', sa.String(length=120), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('game_version',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=40), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('mod',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=80), nullable=False),
    sa.Column('desc', sa.Text(), nullable=False),
    sa.Column('website', sa.String(length=120), nullable=False),
    sa.Column('uuid', mcarch.util.sqla_uuid.GUID(), nullable=False),
    sa.Column('slug', sa.String(length=80), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('slug')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=80), nullable=False),
    sa.Column('password', sa.Binary(), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('totp_secret', sa.String(length=16), nullable=True),
    sa.Column('totp_last_auth', sa.String(length=6), nullable=True),
    sa.Column('role', sa.Enum('user', 'archivist', 'moderator', 'admin', name='userrole'), nullable=False),
    sa.Column('last_seen', sa.DateTime(), nullable=True),
    sa.Column('disabled', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('name')
    )
    op.create_table('log_mod',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=80), nullable=False),
    sa.Column('desc', sa.Text(), nullable=False),
    sa.Column('website', sa.String(length=120), nullable=False),
    sa.Column('uuid', mcarch.util.sqla_uuid.GUID(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('date', sa.DateTime(), nullable=True),
    sa.Column('cur_id', sa.Integer(), nullable=True),
    sa.Column('index', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['cur_id'], ['mod.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('mod_authored_by',
    sa.Column('mod_id', sa.Integer(), nullable=False),
    sa.Column('author_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['author_id'], ['author.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['mod_id'], ['mod.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('mod_id', 'author_id')
    )
    op.create_table('mod_version',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=40), nullable=False),
    sa.Column('desc', sa.Text(), nullable=False),
    sa.Column('url', sa.String(length=120), nullable=False),
    sa.Column('uuid', mcarch.util.sqla_uuid.GUID(), nullable=False),
    sa.Column('mod_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['mod_id'], ['mod.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('reset_token',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('token', mcarch.util.sqla_uuid.GUID(), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=False),
    sa.Column('kind', sa.Enum('password', 'otp', name='resettype'), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('token')
    )
    op.create_table('session',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('sess_id', mcarch.util.sqla_uuid.GUID(), nullable=False),
    sa.Column('login_ip', sa.String(length=128), nullable=False),
    sa.Column('login_date', sa.DateTime(), nullable=False),
    sa.Column('last_seen', sa.DateTime(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('authed_2fa', sa.Boolean(), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('sess_id')
    )
    op.create_table('stored_file',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=80), nullable=False),
    sa.Column('sha256', sa.String(length=130), nullable=False),
    sa.Column('upload_by_id', sa.Integer(), nullable=True),
    sa.Column('b2_path', sa.String(length=300), nullable=True),
    sa.ForeignKeyConstraint(['upload_by_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('draft_mod',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=80), nullable=False),
    sa.Column('desc', sa.Text(), nullable=False),
    sa.Column('website', sa.String(length=120), nullable=False),
    sa.Column('uuid', mcarch.util.sqla_uuid.GUID(), nullable=False),
    sa.Column('archived', sa.Boolean(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('base_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['base_id'], ['log_mod.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('log_mod_authored_by',
    sa.Column('mod_id', sa.Integer(), nullable=False),
    sa.Column('author_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['author_id'], ['author.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['mod_id'], ['log_mod.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('mod_id', 'author_id')
    )
    op.create_table('log_mod_version',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=40), nullable=False),
    sa.Column('desc', sa.Text(), nullable=False),
    sa.Column('url', sa.String(length=120), nullable=False),
    sa.Column('uuid', mcarch.util.sqla_uuid.GUID(), nullable=False),
    sa.Column('mod_id', sa.Integer(), nullable=True),
    sa.Column('cur_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['cur_id'], ['mod_version.id'], ),
    sa.ForeignKeyConstraint(['mod_id'], ['log_mod.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('mod_file',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('desc', sa.Text(), nullable=False),
    sa.Column('uuid', mcarch.util.sqla_uuid.GUID(), nullable=False),
    sa.Column('page_url', sa.String(length=500), nullable=False),
    sa.Column('redirect_url', sa.String(length=500), nullable=False),
    sa.Column('direct_url', sa.String(length=500), nullable=False),
    sa.Column('version_id', sa.Integer(), nullable=True),
    sa.Column('client_classes', sa.String(length=500), nullable=False),
    sa.Column('server_classes', sa.String(length=500), nullable=False),
    sa.Column('resources_dir', sa.String(length=500), nullable=False),
    sa.Column('minecraft_dir', sa.String(length=500), nullable=False),
    sa.Column('redist', sa.Boolean(), nullable=True),
    sa.Column('stored_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['stored_id'], ['stored_file.id'], ),
    sa.ForeignKeyConstraint(['version_id'], ['mod_version.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('mod_version_for_game_version',
    sa.Column('mod_vsn_id', sa.Integer(), nullable=False),
    sa.Column('game_vsn_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['game_vsn_id'], ['game_version.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['mod_vsn_id'], ['mod_version.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('mod_vsn_id', 'game_vsn_id')
    )
    op.create_table('draft_mod_authored_by',
    sa.Column('mod_id', sa.Integer(), nullable=False),
    sa.Column('author_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['author_id'], ['author.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['mod_id'], ['draft_mod.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('mod_id', 'author_id')
    )
    op.create_table('draft_mod_version',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=40), nullable=False),
    sa.Column('desc', sa.Text(), nullable=False),
    sa.Column('url', sa.String(length=120), nullable=False),
    sa.Column('uuid', mcarch.util.sqla_uuid.GUID(), nullable=False),
    sa.Column('mod_id', sa.Integer(), nullable=True),
    sa.Column('base_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['base_id'], ['log_mod_version.id'], ),
    sa.ForeignKeyConstraint(['mod_id'], ['draft_mod.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('log_mod_file',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('desc', sa.Text(), nullable=False),
    sa.Column('uuid', mcarch.util.sqla_uuid.GUID(), nullable=False),
    sa.Column('page_url', sa.String(length=500), nullable=False),
    sa.Column('redirect_url', sa.String(length=500), nullable=False),
    sa.Column('direct_url', sa.String(length=500), nullable=False),
    sa.Column('version_id', sa.Integer(), nullable=True),
    sa.Column('client_classes', sa.String(length=500), nullable=False),
    sa.Column('server_classes', sa.String(length=500), nullable=False),
    sa.Column('resources_dir', sa.String(length=500), nullable=False),
    sa.Column('minecraft_dir', sa.String(length=500), nullable=False),
    sa.Column('cur_id', sa.Integer(), nullable=True),
    sa.Column('stored_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['cur_id'], ['mod_file.id'], ),
    sa.ForeignKeyConstraint(['stored_id'], ['stored_file.id'], ),
    sa.ForeignKeyConstraint(['version_id'], ['log_mod_version.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('log_mod_version_for_game_version',
    sa.Column('mod_vsn_id', sa.Integer(), nullable=False),
    sa.Column('game_vsn_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['game_vsn_id'], ['game_version.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['mod_vsn_id'], ['log_mod_version.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('mod_vsn_id', 'game_vsn_id')
    )
    op.create_table('draft_mod_file',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('desc', sa.Text(), nullable=False),
    sa.Column('uuid', mcarch.util.sqla_uuid.GUID(), nullable=False),
    sa.Column('page_url', sa.String(length=500), nullable=False),
    sa.Column('redirect_url', sa.String(length=500), nullable=False),
    sa.Column('direct_url', sa.String(length=500), nullable=False),
    sa.Column('version_id', sa.Integer(), nullable=True),
    sa.Column('client_classes', sa.String(length=500), nullable=False),
    sa.Column('server_classes', sa.String(length=500), nullable=False),
    sa.Column('resources_dir', sa.String(length=500), nullable=False),
    sa.Column('minecraft_dir', sa.String(length=500), nullable=False),
    sa.Column('base_id', sa.Integer(), nullable=True),
    sa.Column('stored_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['base_id'], ['log_mod_file.id'], ),
    sa.ForeignKeyConstraint(['stored_id'], ['stored_file.id'], ),
    sa.ForeignKeyConstraint(['version_id'], ['draft_mod_version.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('draft_mod_version_for_game_version',
    sa.Column('mod_vsn_id', sa.Integer(), nullable=False),
    sa.Column('game_vsn_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['game_vsn_id'], ['game_version.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['mod_vsn_id'], ['draft_mod_version.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('mod_vsn_id', 'game_vsn_id')
    )

def downgrade():
    op.drop_table('draft_mod_version_for_game_version')
    op.drop_table('draft_mod_file')
    op.drop_table('log_mod_version_for_game_version')
    op.drop_table('log_mod_file')
    op.drop_table('draft_mod_version')
    op.drop_table('draft_mod_authored_by')
    op.drop_table('mod_version_for_game_version')
    op.drop_table('mod_file')
    op.drop_table('log_mod_version')
    op.drop_table('log_mod_authored_by')
    op.drop_table('draft_mod')
    op.drop_table('stored_file')
    op.drop_table('session')
    op.drop_table('reset_token')
    op.drop_table('mod_version')
    op.drop_table('mod_authored_by')
    op.drop_table('log_mod')
    op.drop_table('user')
    op.drop_table('mod')
    op.drop_table('game_version')
    op.drop_table('author')

