from hypothesis import given, strategies as st
import html

# Generate a wide variety of input strings to test html.unescape:
# - Basic strings
# - Strings with valid HTML character references (named, decimal, hex)
# - Strings with invalid HTML character references
# - Empty string
# - Very long strings
# Properties to check based on documentation:
# - Output contains no HTML character references (named, decimal, hex)
# - Output only contains valid Unicode characters
# - unescape is idempotent - applying it again doesn't change output 
@given(st.one_of(
    st.text(),
    st.text() | st.from_regex('&[a-zA-Z0-9]+;'),
    st.text() | st.from_regex('&#[0-9]{1,4};'), 
    st.text() | st.from_regex('&#x[0-9a-fA-F]{1,4};'),
    st.from_regex('&#[0-9]{5,};'),
    st.from_regex('&#x[0-9a-fA-F]{5,};'),
    st.just(''),
    st.text(min_size=1000000)
))
def test_unescape(s):
    escaped = html.unescape(s)
    assert '&' not in escaped
    assert html.unescape(escaped) == escaped
# End program