from collections import defaultdict
from pathlib import Path
import re

from sphinx.util import logging
from sphinxcontrib.bibtex.citation_target import parse_citation_targets

project = "The Growing Wiki"
author = "Gromo Authors"
html_title = "The Growing Wiki"
html_short_title = "The Growing Wiki"

extensions = [
    "sphinxcontrib.bibtex",
]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
bibtex_bibfiles = ["../references.bib"]

html_theme = "furo"
html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_js_files = ["sidebar-open.js"]
numfig = True
html_theme_options = {
    "light_logo": "logo.png",
    "dark_logo": "logo-dark.png",
}

_CITE_ROLE_PATTERN = re.compile(r":cite(?::[a-z]+)?:`([^`]+)`")
_WIKILINK_PATTERN = re.compile(r"(?<!\\)\[\[([^\[\]\n]+?)\]\]")
_INLINE_LITERAL_PATTERN = re.compile(r"(``[^`]*``)")
_CODE_BLOCK_DIRECTIVE_PATTERN = re.compile(
    r"^\s*\.\.\s+(code-block|code|sourcecode|literalinclude|parsed-literal|math)\b.*::\s*$"
)
_UNDERLINE_CHARS = set(r"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~""")
_LOGGER = logging.getLogger(__name__)

# Optional aliases for names that do not match doc titles directly.
_WIKILINK_ALIASES = {
    "technicaloverview": "overview/index",
    "home": "index",
}
_WIKILINK_DOCS_BY_EXACT = {}
_WIKILINK_DOCS_BY_KEY = defaultdict(set)


def _prefix_citation_roles(text, keyprefix):
    def _replace_target(match):
        target = match.group(1)
        try:
            prefixed = []
            for citation in parse_citation_targets(target):
                pre = f"{{{citation.pre}}}" if citation.pre else ""
                post = f"{{{citation.post}}}" if citation.post else ""
                prefixed.append(f"{pre}{keyprefix}{citation.key}{post}")
            return match.group(0).replace(target, ", ".join(prefixed), 1)
        except ValueError:
            return match.group(0)

    return _CITE_ROLE_PATTERN.sub(_replace_target, text)


def _normalize_wikilink_key(value):
    return re.sub(r"[\s_-]+", "", value.strip().lower())


def _extract_rst_title(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    for idx in range(len(lines) - 1):
        title = lines[idx].strip()
        if not title:
            continue

        underline = lines[idx + 1].strip()
        if not underline:
            continue
        if len(set(underline)) != 1:
            continue
        if underline[0] not in _UNDERLINE_CHARS:
            continue
        if len(underline) < len(title):
            continue
        return title
    return None


def _add_wikilink_key(index, key, docname):
    normalized = _normalize_wikilink_key(key)
    if normalized:
        index[normalized].add(docname)


def _build_wikilink_index(app):
    docs_root = Path(app.confdir)
    docs_by_exact = {}
    docs_by_key = defaultdict(set)

    for rst_path in docs_root.rglob("*.rst"):
        rel_path = rst_path.relative_to(docs_root)
        if any(part.startswith("_") for part in rel_path.parts):
            continue

        docname = rel_path.with_suffix("").as_posix()
        docs_by_exact[docname.lower()] = docname

        _add_wikilink_key(docs_by_key, rel_path.stem, docname)
        _add_wikilink_key(docs_by_key, docname, docname)

        title = _extract_rst_title(rst_path)
        if title:
            _add_wikilink_key(docs_by_key, title, docname)

    for alias_key, alias_docname in _WIKILINK_ALIASES.items():
        if alias_docname.lower() in docs_by_exact:
            docs_by_key[_normalize_wikilink_key(alias_key)].add(alias_docname)
        else:
            _LOGGER.warning(
                "WikiLink alias %r points to missing docname %r",
                alias_key,
                alias_docname,
            )

    _WIKILINK_DOCS_BY_EXACT.clear()
    _WIKILINK_DOCS_BY_EXACT.update(docs_by_exact)
    _WIKILINK_DOCS_BY_KEY.clear()
    _WIKILINK_DOCS_BY_KEY.update(docs_by_key)


def _resolve_wikilink_target(raw_target):
    target = raw_target.strip()
    if not target:
        return None, "empty target"

    normalized_path = target.removesuffix(".rst").strip("/").replace("\\", "/")
    exact_match = _WIKILINK_DOCS_BY_EXACT.get(normalized_path.lower())
    if exact_match:
        return exact_match, None

    normalized_key = _normalize_wikilink_key(target)
    if not normalized_key:
        return None, "empty target"

    candidates = sorted(_WIKILINK_DOCS_BY_KEY.get(normalized_key, set()))
    if not candidates:
        return None, f"unknown target {target!r}"
    if len(candidates) > 1:
        return None, (
            f"ambiguous target {target!r}; candidates: {', '.join(candidates)} "
            "(use explicit docname, e.g. [[Label|path/to/docname]])"
        )
    return candidates[0], None


def _replace_wikilinks_in_text_segment(segment, docname, line_number):
    def _replace(match):
        token = match.group(1).strip()
        if "|" in token:
            label, target = token.split("|", 1)
            label = label.strip()
            target = target.strip()
        else:
            label = token
            target = token

        resolved_docname, error = _resolve_wikilink_target(target)
        if error:
            _LOGGER.warning(
                "Unresolved WikiLink %r in %s: %s",
                token,
                docname,
                error,
                location=(docname, line_number),
            )
            return match.group(0)

        if resolved_docname == docname:
            return label

        safe_label = label.replace("`", r"\`")
        return f":doc:`{safe_label} </{resolved_docname}>`"

    return _WIKILINK_PATTERN.sub(_replace, segment)


def _replace_wikilinks(docname, text):
    if "[[" not in text or not _WIKILINK_DOCS_BY_EXACT:
        return text

    output_lines = []
    in_literal_block_indent = None
    pending_literal_indent = None

    for line_number, raw_line in enumerate(text.splitlines(keepends=True), start=1):
        line_ending = "\n" if raw_line.endswith("\n") else ""
        line = raw_line[:-1] if line_ending else raw_line
        stripped = line.strip()
        indent = len(line) - len(line.lstrip(" "))

        if in_literal_block_indent is not None:
            if not stripped or indent > in_literal_block_indent:
                output_lines.append(raw_line)
                continue
            in_literal_block_indent = None

        if pending_literal_indent is not None:
            if not stripped:
                output_lines.append(raw_line)
                continue
            if indent > pending_literal_indent:
                in_literal_block_indent = pending_literal_indent
                output_lines.append(raw_line)
                continue
            pending_literal_indent = None

        if _CODE_BLOCK_DIRECTIVE_PATTERN.match(line):
            output_lines.append(raw_line)
            in_literal_block_indent = indent
            continue

        rebuilt_parts = []
        for part in _INLINE_LITERAL_PATTERN.split(line):
            if part.startswith("``") and part.endswith("``"):
                rebuilt_parts.append(part)
            else:
                rebuilt_parts.append(
                    _replace_wikilinks_in_text_segment(part, docname, line_number)
                )

        rebuilt_line = "".join(rebuilt_parts)
        output_lines.append(rebuilt_line + line_ending)

        if rebuilt_line.rstrip().endswith("::") and not line.lstrip().startswith(".. "):
            pending_literal_indent = indent

    return "".join(output_lines)


def setup(app):
    # Some furo/Sphinx combinations can pass meta=None to templates.
    # Ensure it is always a dict so template access via meta.get(...) is safe.
    def _ensure_meta(_app, _pagename, _templatename, context, _doctree):
        if context.get("meta") is None:
            context["meta"] = {}

    def _on_builder_inited(_app):
        _build_wikilink_index(_app)

    # Expand custom WikiLinks, then append a local bibliography on pages using citations.
    def _process_source(_app, docname, source):
        text = _replace_wikilinks(docname, source[0])

        if ":cite:" not in text:
            source[0] = text
            return
        if ".. bibliography::" in text:
            source[0] = text
            return

        keyprefix = f"{docname.replace('/', '_')}__"
        text = _prefix_citation_roles(text, keyprefix)
        source[0] = (
            text.rstrip()
            + "\n\nReferences\n~~~~~~~~~~\n\n.. bibliography::\n"
            + "   :filter: docname in docnames\n"
            + f"   :keyprefix: {keyprefix}\n"
        )

    app.connect("html-page-context", _ensure_meta)
    app.connect("builder-inited", _on_builder_inited)
    app.connect("source-read", _process_source)
