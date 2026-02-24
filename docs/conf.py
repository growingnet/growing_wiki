project = 'The Growing Library'
author = 'Alex Davey'
html_title = 'The Growing Library'
html_short_title = 'The Growing Library'

extensions = []
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'furo'
html_static_path = ['_static']
html_css_files = ['custom.css']
html_js_files = ['sidebar-open.js']
html_theme_options = {
    'light_logo': 'logo.png',
    'dark_logo': 'logo-dark.png',
}


def setup(app):
    # Some furo/Sphinx combinations can pass meta=None to templates.
    # Ensure it is always a dict so template access via meta.get(...) is safe.
    def _ensure_meta(_app, _pagename, _templatename, context, _doctree):
        if context.get('meta') is None:
            context['meta'] = {}

    app.connect('html-page-context', _ensure_meta)
