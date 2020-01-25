from flask import request

from mcarch.login import cur_user

def unless_cur_user(*args, **kwargs):
    """Use as the `unless` for caching. This will skip the cache if the user is logged in."""
    return bool(cur_user())

