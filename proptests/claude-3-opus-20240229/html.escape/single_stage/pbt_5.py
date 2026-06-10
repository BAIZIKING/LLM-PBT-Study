from hypothesis import given, strategies as st
from html import escape

# Generate a wide variety of strings to test html.escape.
# Include plain strings, strings with characters that should be escaped,
# strings with characters that shouldn't be escaped, and empty string.
# Sometimes generate strings with quote=True, sometimes with quote=False.
@given(st.one_of(
    st.text(),  
    st.just(''),
    st.sampled_from(['&', '<', '>', '"', "'"]),
    st.just('&<>'),
    st.just('"'),
    st.just("'")
), 
quote=st.booleans())
def test_html_escape(s, quote):
    escaped = escape(s, quote=quote)
    
    # Check '&', '<' and '>' are always escaped
    assert '&' not in escaped or '&amp;' in escaped
    assert '<' not in escaped or '&lt;' in escaped
    assert '>' not in escaped or '&gt;' in escaped

    # Check '"' and "'" are escaped when quote=True
    if quote:
        assert '"' not in escaped or '&quot;' in escaped
        assert "'" not in escaped or '&#x27;' in escaped
    
    # Check escaping is minimal - characters that don't need escaping are unchanged
    for c in s:
        if c not in ('&', '<', '>', '"', "'"):
            assert c in escaped

# End program