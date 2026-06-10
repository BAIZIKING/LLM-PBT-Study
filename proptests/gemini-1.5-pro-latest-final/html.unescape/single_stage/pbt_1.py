from hypothesis import given, strategies as st
import html

# Summary: Generates random strings and strings with HTML entities for testing
@given(st.text(alphabet=st.characters(blacklist_categories=('C')) | 
                 st.from_regex(r'&[#\w]+;?', fullmatch=True),
                 min_size=1))
def test_html_unescape(s):
    unescaped_string = html.unescape(s)
    # Check if the output is a string
    assert isinstance(unescaped_string, str)
    # Check if valid entities are decoded
    assert unescaped_string.find('&') == -1
    # Check idempotence
    assert html.unescape(unescaped_string) == unescaped_string
# End program