"""
HTML Sanitizer - Policy-based HTML sanitization library.

Provides configurable policies to allow specific HTML elements and attributes
while stripping dangerous content.
"""

import re
import cgi


class Policy(object):
    """
    Policy defines what HTML elements and attributes are permitted
    in sanitized output.
    """

    # Elements that contain raw text (not parsed as nested HTML)
    RAWTEXT_ELEMENTS = frozenset(['style', 'xmp', 'iframe', 'noembed',
                                   'noframes', 'noscript', 'plaintext'])

    def __init__(self):
        self._allowed_elements = set()
        self._allowed_attributes = set()
        self._allow_unsafe = False

    def allow_elements(self, *elements):
        """Add elements to the allow list."""
        for el in elements:
            self._allowed_elements.add(el.lower())
        return self

    def allow_attributes(self, *attributes):
        """Add attributes to the allow list."""
        for attr in attributes:
            self._allowed_attributes.add(attr.lower())
        return self

    def allow_unsafe(self, val=True):
        """Enable allowing unsafe elements like script. Use with caution."""
        self._allow_unsafe = val
        return self

    def sanitize(self, html_input):
        """
        Sanitize the provided HTML string according to this policy.
        Returns the sanitized HTML string with disallowed elements removed.
        """
        if not html_input:
            return ''
        return _sanitize(self, html_input)


def _sanitize(policy, html_input):
    """
    Process HTML input token by token, applying the sanitization policy.
    Uses a tokenizer approach similar to Go's html.Tokenizer for consistency.
    """
    output = []
    pos = 0
    length = len(html_input)
    skip_depth = 0
    in_raw_text = False
    raw_text_tag = None

    # Regex patterns for tokenizing
    tag_pattern = re.compile(
        r'<(/?)(\w+)((?:\s+[\w-]+(?:\s*=\s*(?:"[^"]*"|\'[^\']*\'|[^\s>]*))?)*)\s*(/?)>',
        re.IGNORECASE | re.DOTALL
    )

    while pos < length:
        match = tag_pattern.search(html_input, pos)

        if not match:
            # No more tags; handle remaining text
            text = html_input[pos:]
            if in_raw_text:
                output.append(text)
            elif skip_depth == 0:
                output.append(cgi.escape(text))
            break

        # Handle text before this tag
        if match.start() > pos:
            text = html_input[pos:match.start()]
            if in_raw_text:
                output.append(text)
            elif skip_depth == 0:
                output.append(cgi.escape(text))

        is_closing = match.group(1) == '/'
        tag_name = match.group(2).lower()
        attrs_str = match.group(3)
        is_self_closing = match.group(4) == '/'

        if in_raw_text:
            # In raw text mode, only the matching closing tag exits the mode
            if is_closing and tag_name == raw_text_tag:
                in_raw_text = False
                raw_text_tag = None
                if tag_name in policy._allowed_elements:
                    output.append('</{}>'.format(tag_name))
            else:
                # Everything else inside raw text is passed through verbatim
                output.append(match.group(0))
            pos = match.end()
            continue

        if is_closing:
            if skip_depth > 0:
                skip_depth -= 1
            elif tag_name in policy._allowed_elements:
                output.append('</{}>'.format(tag_name))
            pos = match.end()
            continue

        # Opening tag
        is_dangerous = (tag_name == 'script' and not policy._allow_unsafe)

        if skip_depth > 0:
            if is_dangerous or tag_name not in policy._allowed_elements:
                if not is_self_closing:
                    skip_depth += 1
            pos = match.end()
            continue

        if is_dangerous:
            if not is_self_closing:
                skip_depth += 1
            pos = match.end()
            continue

        if tag_name in policy._allowed_elements:
            filtered = _filter_attributes(policy, attrs_str)
            if is_self_closing:
                output.append('<{}{} />'.format(tag_name, filtered))
            else:
                output.append('<{}{}>'.format(tag_name, filtered))

                # If this element is a raw text element, enter raw text mode
                # The content of these elements is not parsed as HTML
                if tag_name in Policy.RAWTEXT_ELEMENTS:
                    in_raw_text = True
                    raw_text_tag = tag_name
        else:
            if not is_self_closing:
                skip_depth += 1

        pos = match.end()

    return ''.join(output)


def _filter_attributes(policy, attrs_str):
    """Parse and filter attributes, keeping only allowed ones."""
    if not attrs_str or not attrs_str.strip():
        return ''

    attr_pattern = re.compile(
        r'([\w-]+)(?:\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|(\S+)))?',
        re.IGNORECASE
    )

    filtered = []
    for m in attr_pattern.finditer(attrs_str):
        attr_name = m.group(1).lower()

        # Always strip event handler attributes
        if attr_name.startswith('on'):
            continue

        if attr_name in policy._allowed_attributes:
            if m.group(2) is not None:
                filtered.append('{}="{}"'.format(attr_name,
                    cgi.escape(m.group(2), quote=True)))
            elif m.group(3) is not None:
                filtered.append("{}='{}'".format(attr_name,
                    cgi.escape(m.group(3), quote=True)))
            elif m.group(4) is not None:
                filtered.append('{}="{}"'.format(attr_name,
                    cgi.escape(m.group(4), quote=True)))
            else:
                filtered.append(attr_name)

    if filtered:
        return ' ' + ' '.join(filtered)
    return ''
