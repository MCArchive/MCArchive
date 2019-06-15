from urllib.parse import urlparse, urljoin
from flask import request, url_for

# from http://flask.pocoo.org/snippets/62/
# ensures a redirect URL leads back to the same host to prevent open redirects
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

