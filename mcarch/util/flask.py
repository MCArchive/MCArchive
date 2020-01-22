"""This file contains some utility functions for working with flask, many of
which are exposed for use in jinja templates."""

import bleach
from markdown import markdown
from datetime import datetime
from flask import Markup, request

#### Functions ####

def is_cur_page(url):
    """Takes a URL and checks if the current page is at that URL."""
    path = request.full_path.strip('?')
    return path == url

def register_conproc(app):
    """
    Registers a context processor with the flask app which provides access to the following
    functions within jinja templates:

    `is_cur_page`
    """
    @app.context_processor
    def inject():
        return dict(
            is_cur_page=is_cur_page
        )


#### Filters ####

# From http://flask.pocoo.org/snippets/33/
def timesince(dt, default="just now", none='never'):
    """
    Returns string representing "time since" e.g.
    3 days ago, 5 hours ago etc.
    """
    if dt is None: return none

    now = datetime.utcnow()
    diff = now - dt
    
    periods = (
        (diff.days / 365, "year", "years"),
        (diff.days / 30, "month", "months"),
        (diff.days / 7, "week", "weeks"),
        (diff.days, "day", "days"),
        (diff.seconds / 3600, "hour", "hours"),
        (diff.seconds / 60, "minute", "minutes"),
        (diff.seconds, "second", "seconds"),
    )

    for period, singular, plural in periods:
        if period >= 1:
            return "%d %s ago" % (period, singular if int(period) == 1 else plural)

    return default

BLEACH_WHITELIST = bleach.sanitizer.ALLOWED_TAGS + [
        "p", "h1", "h2", "h3", "h4", "h5", "h6", "br"
    ]

def safe_markdown(md):
    """
    This filter renders the input as markdown nd then cleans the output with bleach.

    Output will be HTML with only safe, white-listed tags.
    """
    return Markup(bleach.clean(markdown(md),
        tags=BLEACH_WHITELIST))

def register_filters(app):
    app.template_filter('timesince')(timesince)
    app.template_filter('safe_markdown')(safe_markdown)

