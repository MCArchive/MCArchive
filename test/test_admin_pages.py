from flask import url_for
from helpers.login import login_as, log_out, check_allowed

def test_reset_pass(client, sample_users):
    login_as(client, sample_users['admin'])


def test_admin_page_perms(client, sample_users):
    page = url_for('admin.main')
    check_allowed(client, sample_users['user'], page, expect=False)
    check_allowed(client, sample_users['archivist'], page, expect=True)
    check_allowed(client, sample_users['moderator'], page, expect=True)
    check_allowed(client, sample_users['admin'], page, expect=True)

def test_changes_page_perms(client, sample_users):
    page = url_for('admin.changes')
    check_allowed(client, sample_users['user'], page, expect=False)
    check_allowed(client, sample_users['archivist'], page, expect=False)
    check_allowed(client, sample_users['moderator'], page, expect=True)
    check_allowed(client, sample_users['admin'], page, expect=True)

def test_files_page_perms(client, sample_users):
    page = url_for('admin.files')
    check_allowed(client, sample_users['user'], page, expect=False)
    check_allowed(client, sample_users['archivist'], page, expect=False)
    check_allowed(client, sample_users['moderator'], page, expect=False)
    check_allowed(client, sample_users['admin'], page, expect=True)

def test_users_page_perms(client, sample_users):
    page = url_for('admin.users')
    check_allowed(client, sample_users['user'], page, expect=False)
    check_allowed(client, sample_users['archivist'], page, expect=False)
    check_allowed(client, sample_users['moderator'], page, expect=False)
    check_allowed(client, sample_users['admin'], page, expect=True)

def test_reset_pass_perms(client, sample_users):
    page = url_for('admin.reset_passwd', name='admin')
    check_allowed(client, sample_users['user'], page, expect=False)
    check_allowed(client, sample_users['archivist'], page, expect=False)
    check_allowed(client, sample_users['moderator'], page, expect=False)
    check_allowed(client, sample_users['admin'], page, expect=True)

def test_reset_2fa_perms(client, sample_users):
    page = url_for('admin.reset_2fa', name='admin')
    check_allowed(client, sample_users['user'], page, expect=False)
    check_allowed(client, sample_users['archivist'], page, expect=False)
    check_allowed(client, sample_users['moderator'], page, expect=False)
    check_allowed(client, sample_users['admin'], page, expect=True)

def test_disable_user_perms(client, sample_users):
    page = url_for('admin.disable_user', name='admin')
    check_allowed(client, sample_users['user'], page, expect=False)
    check_allowed(client, sample_users['archivist'], page, expect=False)
    check_allowed(client, sample_users['moderator'], page, expect=False)
    check_allowed(client, sample_users['admin'], page, expect=True)

def test_new_user_perms(client, sample_users):
    page = url_for('admin.new_user')
    check_allowed(client, sample_users['user'], page, expect=False)
    check_allowed(client, sample_users['archivist'], page, expect=False)
    check_allowed(client, sample_users['moderator'], page, expect=False)
    check_allowed(client, sample_users['admin'], page, expect=True)

def test_edit_user_perms(client, sample_users):
    page = url_for('admin.edit_user', name='admin')
    check_allowed(client, sample_users['user'], page, expect=False)
    check_allowed(client, sample_users['archivist'], page, expect=False)
    check_allowed(client, sample_users['moderator'], page, expect=False)
    check_allowed(client, sample_users['admin'], page, expect=True)

