import re

from sphinxcontrib.bibtex.citation_target import parse_citation_targets

project = 'The Growing Library'
author = 'Gromo Authors'
html_title = 'The Growing Library'
html_short_title = 'The Growing Library'

extensions = [
    'sphinxcontrib.bibtex',
]
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
bibtex_bibfiles = ['../ijcai26_shorten.bib']

html_theme = 'furo'
html_static_path = ['_static']
html_css_files = ['custom.css']
html_js_files = ['sidebar-open.js']
html_theme_options = {
    'light_logo': 'logo.png',
    'dark_logo': 'logo-dark.png',
}

_CITE_ROLE_PATTERN = re.compile(r":cite(?::[a-z]+)?:`([^`]+)`")


def _prefix_citation_roles(text, keyprefix):
    def _replace_target(match):
        target = match.group(1)
        try:
            prefixed = []
            for citation in parse_citation_targets(target):
                pre = f'{{{citation.pre}}}' if citation.pre else ''
                post = f'{{{citation.post}}}' if citation.post else ''
                prefixed.append(f'{pre}{keyprefix}{citation.key}{post}')
            return match.group(0).replace(target, ', '.join(prefixed), 1)
        except ValueError:
            return match.group(0)

    return _CITE_ROLE_PATTERN.sub(_replace_target, text)


def setup(app):
    # Some furo/Sphinx combinations can pass meta=None to templates.
    # Ensure it is always a dict so template access via meta.get(...) is safe.
    def _ensure_meta(_app, _pagename, _templatename, context, _doctree):
        if context.get('meta') is None:
            context['meta'] = {}

    # Append a local bibliography on pages that use citations.
    def _append_local_bibliography(_app, docname, source):
        text = source[0]
        if ':cite:' not in text:
            return
        if '.. bibliography::' in text:
            return
        keyprefix = f'{docname.replace("/", "_")}__'
        text = _prefix_citation_roles(text, keyprefix)
        source[0] = (
            text.rstrip()
            + '\n\nReferences\n~~~~~~~~~~\n\n.. bibliography::\n'
            + '   :filter: docname in docnames\n'
            + f'   :keyprefix: {keyprefix}\n'
        )

    app.connect('html-page-context', _ensure_meta)
    app.connect('source-read', _append_local_bibliography)
