project = 'growing_docs'
author = 'Alex Davey'

extensions = []
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'furo'


def setup(app):
    # Some furo/Sphinx combinations can pass meta=None to templates.
    # Ensure it is always a dict so template access via meta.get(...) is safe.
    def _ensure_meta(_app, _pagename, _templatename, context, _doctree):
        if context.get('meta') is None:
            context['meta'] = {}

    app.connect('html-page-context', _ensure_meta)
