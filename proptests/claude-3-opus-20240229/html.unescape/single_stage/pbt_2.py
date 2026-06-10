from hypothesis import given, strategies as st
import html

# Generate a wide variety of test inputs including:
# - Empty string 
# - Strings with no escape sequences
# - Strings with valid named escape sequences like &gt;
# - Strings with valid numeric escape sequences like &#62; or &#x3e;  
# - Strings with invalid escape sequences
# - Very long strings
@given(st.text())
def test_html_unescape(s):
    # html.unescape should handle empty string
    if len(s) == 0:
        assert html.unescape(s) == ""
    
    # Result should be same or longer than input (escape sequences expanded)
    assert len(html.unescape(s)) >= len(s)
    
    # Escaping then unescaping should give original string
    assert html.unescape(html.escape(s)) == s
    
    # Unescaping should never raise exceptions 
    try:
        html.unescape(s)
    except Exception:
        assert False, "Exception raised when unescaping"
# End program