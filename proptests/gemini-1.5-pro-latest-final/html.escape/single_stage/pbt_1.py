from hypothesis import given, strategies as st
import html

# Summary: The generation strategy aims to create a diverse range of inputs for `html.escape`, including:
# - Strings with varying lengths and character compositions.
# - Special characters like &, <, >, ", and '.
# - Unicode characters to ensure comprehensive testing.
# - Edge cases like empty strings and strings containing only special characters.
@given(st.text(alphabet=st.characters(blacklist_characters=["\n", "\r"]), min_size=0))
def test_html_escape(s):
    escaped_string = html.escape(s)
    # Property 1: Check if &, <, and > are escaped correctly.
    assert "&" not in escaped_string
    assert "<" not in escaped_string
    assert ">" not in escaped_string

    # Property 2: If quote=True, verify if " and ' are also escaped.
    if html.escape(s, quote=True):
        assert '"' not in escaped_string
        assert "'" not in escaped_string
# End program