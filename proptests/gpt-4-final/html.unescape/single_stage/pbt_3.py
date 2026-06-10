from hypothesis import given, strategies as st
import html

# Generate strings containing possible named or numeric character references
@given(st.one_of(
    st.text(min_size=1).map(lambda s: '&{};'.format(s)),
    st.integers(min_value=0, max_value=0x10FFFF).map(lambda i: '&#{};'.format(i)),
    st.integers(min_value=0, max_value=0x10FFFF).map(lambda i: '&#x{:X};'.format(i))
))
def test_html_unescape(s):
    actual = html.unescape(s)
    expected = s.replace('&gt;', '>').replace('&lt;', '<').replace('&amp;', '&')  # replace other character references as per HTML5 standard
    assert actual == expected