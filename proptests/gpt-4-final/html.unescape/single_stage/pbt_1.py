from hypothesis import given, strategies as st
from html import unescape

# Summary: Generate strings with a variety of HTML character references.
@given(st.text(min_size=0, alphabet=st.characters(whitelist_categories=("Nd", "No", "Cc", "&#", ";"))))
def test_html_unescape(html_encoded_string):
    unicode_string = unescape(html_encoded_string)

    # Property 1: The function should return a string
    assert isinstance(unicode_string, str)

    # Property 2: If we escape the output, it should return the same as original input except for invalid references
    assert unescape(unicode_string) == unicode_string

    # Property 3: For strings without any recognizable HTML character references, the output should be the same as the input.
    if "&#;" not in html_encoded_string:
        assert unicode_string == html_encoded_string