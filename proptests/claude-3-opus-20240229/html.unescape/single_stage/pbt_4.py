from hypothesis import given, strategies as st
import html

# Generate a wide variety of strings to test html.unescape:
# - valid named char refs like &gt; 
# - valid decimal numeric char refs like &#62;
# - valid hex numeric char refs like &#x3E; 
# - mix of valid and invalid refs
# - edge cases like empty string, whitespace, non-ref & and # chars
@given(st.text(min_size=0, max_size=100))
def test_html_unescape(s):
    unescaped = html.unescape(s)
    assert '&' not in unescaped  # no refs should remain after unescaping
    assert isinstance(unescaped, str)  # result should still be a string
    assert len(unescaped) >= len(s)  # unescaped should be at least as long as input
# End program