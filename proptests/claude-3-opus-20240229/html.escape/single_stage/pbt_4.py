from hypothesis import given, strategies as st
import html

# Generate a wide variety of strings including common characters that need escaping 
# like &, <, >, ", ', as well as strings with no escapable characters.
# Use whitespace characters and other printable ascii characters to create 
# more variation in the generated strings.
@given(st.text(alphabet=st.characters(min_codepoint=32, max_codepoint=126), min_size=0, max_size=100))
def test_html_escape(s):
    escaped = html.escape(s)
    
    # Check that & < > are always escaped 
    assert '&' not in escaped or '&amp;' in escaped
    assert '<' not in escaped or '&lt;' in escaped
    assert '>' not in escaped or '&gt;' in escaped
    
    # Check that " ' are escaped when quote is True (default)
    assert '"' not in escaped or '&quot;' in escaped
    assert "'" not in escaped or '&#x27;' in escaped

    # Check that escaping is idempotent - escaping again does not change the result
    assert html.escape(escaped) == escaped
# End program