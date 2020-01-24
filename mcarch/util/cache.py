from flask import request

from mcarch.login import cur_user

def mk_cache_key(*args, **kwargs):
    """Use as `key_prefix` for caching. This includes URL parameters in the cache key."""
    # modified from https://stackoverflow.com/questions/9413566/flask-cache-memoize-url-query-string-parameters-as-well
    path = request.path
    args = str(hash(frozenset(request.args.items())))
    return path + args

def unless_cur_user(*args, **kwargs):
    """Use as the `unless` for caching. This will skip the cache if the user is logged in."""
    return bool(cur_user())

