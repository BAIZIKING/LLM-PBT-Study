from hypothesis import given, strategies as st
import html

# Generate a wide variety of strings to test html.unescape:
# - Basic strings
# - Strings with valid named character refs like &gt;
# - Strings with valid numeric character refs like &#62; or &#x3e; 
# - Strings with invalid character refs
# - Empty string
# The decoded string should have all character refs converted to 
# the corresponding Unicode characters, per the HTML5 standard.
@given(st.one_of(
    st.text(), 
    st.from_regex(r'.*&[a-z]+;.*', fullmatch=True),
    st.from_regex(r'.*&#\d+;.*', fullmatch=True),
    st.from_regex(r'.*&#x[a-f0-9]+;.*', fullmatch=True),
    st.from_regex(r'.*&\w+;.*', fullmatch=True),
    st.just(''),
))
def test_html_unescape(s):
    decoded = html.unescape(s)
    assert '&' not in decoded  # All & should be decoded
    assert type(decoded) == str
    if '&' not in s:
        assert s == decoded  # Decoding valid string shouldn't change it
# End program