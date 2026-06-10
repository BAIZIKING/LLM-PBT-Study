from hypothesis import given, strategies as st
from html import unescape

# Summary: Generates strings with various character types and escape sequences
@given(st.text(alphabet=st.characters(blacklist_categories=('C',)), allow_unicode=True))
def test_html_unescape(text):
    # Idempotence
    assert unescape(unescape(text)) == unescape(text)

    # Inverse of html.escape (for valid sequences)
    escaped = escape(text, quote=True)
    assert unescape(escaped) == text

    # Correctness (spot-checking a few common escapes)
    assert unescape("&amp;") == "&"
    assert unescape("&#60;") == "<"
    assert unescape("&#x3e;") == ">"

    # Handling of invalid references (implementation specific)
    # Check if invalid references are ignored, replaced, or raise an error
    # For example, if they are replaced with �:
    assert unescape("&#invalid;") == "�"

# End program