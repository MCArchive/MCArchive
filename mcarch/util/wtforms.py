"""Useful stuff for WTForms"""

import json
from wtforms import StringField
from wtforms.widgets import TextInput, Select, HTMLString


# From: https://www.julo.ch/blog/wtforms-chosen/
# modified to work with choices.js instead

class BetterSelect(Select):
    def __init__(self, multiple=False, renderer=None, render_js=True, options={}):
        """
            Initiate the widget. This offers you two general options.
            First off it allows you to configure the BetterSelect to
            allow multiple options and it allows you to pass options
            to the choices select (this will produce a json object)
            that choices will get passed as configuration.

                :param multiple: whether this is a multiple select
                    (default to `False`)
                :param renderer: If you do not want to use the default
                    select renderer, you can pass a function that will
                    get the field and options as arguments so that
                    you can customize the rendering.
                :param options: a dictionary of options that will
                    influence the choices behavior.
        """
        super(BetterSelect, self).__init__(multiple=multiple)
        self.renderer = renderer
        self.render_js = render_js
        options.setdefault('removeItemButton', multiple)
        self.options = options

    def __call__(self, field, **kwargs):
        """
            Render the actual select.

                :param field: the field to render
                :param **kwargs: options to pass to the rendering
                    (i.e. class, data-* and so on)

            This will render the select as is and attach a choices
            initiator script for the given id afterwards considering
            the options set up in the beginning.
        """
        kwargs.setdefault('id', field.id)

        html = []
        # render the select
        if self.renderer:
            html.append(self.renderer(self, field, **kwargs))
        else:
            html.append(super(BetterSelect, self).__call__(field, **kwargs))
        # attach the choices initiation with options
        if self.render_js:
            html.append(
                """<script>new Choices("#%s", %s);</script>\n"""
                % (kwargs['id'], json.dumps(self.options))
            )
        # return the HTML (as safe markup)
        return HTMLString('\n'.join(html))


class TagInput(TextInput):
    """
    This Widget offers a tag input box based on Choices.js.
    """
    def __init__(self, renderer=None, options={}):
        """
            Initiate the widget. This offers you two general options.
            First off it allows you to configure the TagInput to
            allow multiple options and it allows you to pass options
            to the choices select (this will produce a json object)
            that choices will get passed as configuration.

                :param renderer: If you do not want to use the default
                    select renderer, you can pass a function that will
                    get the field and options as arguments so that
                    you can customize the rendering.
                :param options: a dictionary of options that will
                    influence the choices behavior.
        """
        super(TagInput, self).__init__()
        self.renderer = renderer
        options.setdefault('removeItemButton', True)
        self.options = options

    def __call__(self, field, **kwargs):
        """
            Render the actual tag input.

                :param field: the field to render
                :param **kwargs: options to pass to the rendering
                    (i.e. class, data-* and so on)

            This will render the tag input as is and attach a choices
            initiator script for the given id afterwards.
        """
        kwargs.setdefault('id', field.id)

        html = []
        # render the select
        if self.renderer:
            html.append(self.renderer(self, field, **kwargs))
        else:
            html.append(super(TagInput, self).__call__(field, **kwargs))
        # attach the choices initiation with options
        html.append(
            """<script>new Choices("#%s", %s);</script>\n"""
            % (kwargs['id'], json.dumps(self.options))
        )
        # return the HTML (as safe markup)
        return HTMLString('\n'.join(html))

