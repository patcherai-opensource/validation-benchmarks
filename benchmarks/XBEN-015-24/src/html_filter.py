"""
HTML Content Filter

A tag-based HTML sanitizer that enforces an allowlist policy.
Parses HTML tokens and strips disallowed elements while preserving
allowed content and structure.
"""

import re

try:
    from html.parser import HTMLParser
except ImportError:
    from HTMLParser import HTMLParser


class ContentFilter(object):
    """
    ContentFilter provides HTML sanitization by enforcing an element and
    attribute allowlist. Elements not in the allowlist are stripped, and
    their content is handled based on the element type.

    Elements whose content should be suppressed if the element itself
    is not allowed (e.g. script, iframe, noscript, object) have their
    inner content removed along with the tags.
    """

    # Elements whose content should be suppressed if the element is not allowed
    SKIP_CONTENT_ELEMENTS = frozenset([
        'script', 'iframe', 'noscript', 'object', 'embed',
        'frame', 'frameset', 'noframes', 'noembed', 'title',
        'style',
    ])

    # Elements that are valid without any attributes
    VOID_ATTR_ELEMENTS = frozenset([
        'b', 'i', 'em', 'strong', 'p', 'br', 'span', 'div', 'section',
        'article', 'aside', 'header', 'footer', 'nav', 'main',
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'ul', 'ol', 'li', 'dl', 'dt', 'dd',
        'table', 'tr', 'td', 'th', 'thead', 'tbody', 'tfoot', 'caption',
        'blockquote', 'pre', 'code', 'hr', 'figure', 'figcaption',
        'a', 'img', 'abbr', 'cite', 'mark', 'small', 'sub', 'sup',
        'ruby', 'rt', 'rp', 'wbr', 'details', 'summary', 'time',
        'select', 'option', 'optgroup', 'style',
    ])

    # Tags that use raw text rendering (content should not be HTML-escaped)
    RAW_TEXT_ELEMENTS = frozenset(['script', 'style'])

    def __init__(self):
        self._allowed_elements = set()
        self._allowed_attributes = set()

    def allow_elements(self, *elements):
        for el in elements:
            self._allowed_elements.add(el.lower())

    def allow_attributes(self, *attributes):
        for attr in attributes:
            self._allowed_attributes.add(attr.lower())

    def sanitize(self, html_input):
        if not html_input or not html_input.strip():
            return html_input

        handler = _SanitizeHandler(
            allowed_elements=self._allowed_elements,
            allowed_attributes=self._allowed_attributes,
            skip_content_elements=self.SKIP_CONTENT_ELEMENTS,
            void_attr_elements=self.VOID_ATTR_ELEMENTS,
            raw_text_elements=self.RAW_TEXT_ELEMENTS,
        )
        try:
            handler.feed(html_input)
        except Exception:
            return ''
        return handler.get_output()


class _SanitizeHandler(HTMLParser):
    """
    Internal HTML token handler that walks through the parsed HTML and
    builds sanitized output according to the policy.
    """

    CDATA_CONTENT_ELEMENTS = ('script', 'style')

    def __init__(self, allowed_elements, allowed_attributes,
                 skip_content_elements, void_attr_elements, raw_text_elements):
        HTMLParser.__init__(self)
        self._allowed_elements = allowed_elements
        self._allowed_attributes = allowed_attributes
        self._skip_content_elements = skip_content_elements
        self._void_attr_elements = void_attr_elements
        self._raw_text_elements = raw_text_elements

        self._output = []
        self._skip_content = False
        self._skip_depth = 0
        self._closing_tags_to_skip = []
        self._most_recent_started = ''

    def get_output(self):
        return ''.join(self._output)

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        self._most_recent_started = tag

        if tag in self._allowed_elements:
            filtered_attrs = self._filter_attrs(attrs)

            if not filtered_attrs and tag not in self._void_attr_elements:
                self._closing_tags_to_skip.append(tag)
                return

            if not self._skip_content:
                self._output.append(self._build_tag(tag, filtered_attrs))
        else:
            if tag in self._skip_content_elements:
                self._skip_content = True
                self._skip_depth += 1
            return

    def handle_endtag(self, tag):
        tag = tag.lower()

        if self._most_recent_started == tag:
            self._most_recent_started = ''

        if self._closing_tags_to_skip and self._closing_tags_to_skip[-1] == tag:
            self._closing_tags_to_skip.pop()
            return

        if tag not in self._allowed_elements:
            if tag in self._skip_content_elements:
                self._skip_depth -= 1
                if self._skip_depth <= 0:
                    self._skip_content = False
                    self._skip_depth = 0
            return

        if not self._skip_content:
            self._output.append('</' + tag + '>')

    def handle_data(self, data):
        if not self._skip_content:
            if self._most_recent_started in self._raw_text_elements:
                # For raw text elements like style, preserve content without escaping.
                # This is necessary to keep CSS intact within style tags.
                self._output.append(data)
            else:
                self._output.append(self._escape_text(data))

    def handle_entityref(self, name):
        if not self._skip_content:
            self._output.append('&' + name + ';')

    def handle_charref(self, name):
        if not self._skip_content:
            self._output.append('&#' + name + ';')

    def handle_comment(self, data):
        pass

    def handle_decl(self, decl):
        pass

    def handle_pi(self, data):
        pass

    def unknown_decl(self, data):
        pass

    def _filter_attrs(self, attrs):
        filtered = []
        for name, value in attrs:
            if name.lower() in self._allowed_attributes:
                if value is None:
                    filtered.append((name, None))
                else:
                    safe_val = value.replace('"', '&quot;')
                    filtered.append((name, safe_val))
        return filtered

    def _build_tag(self, tag, attrs):
        parts = ['<' + tag]
        for name, value in attrs:
            if value is None:
                parts.append(' ' + name)
            else:
                parts.append(' ' + name + '="' + value + '"')
        parts.append('>')
        return ''.join(parts)

    def _escape_text(self, text):
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        return text
