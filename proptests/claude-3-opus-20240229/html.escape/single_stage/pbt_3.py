from hypothesis import given, strategies as st
import html

# Generate a wide variety of string inputs to test html.escape:
# - Use st.text() to generate random Unicode strings
# - Include some strings with &, <, >, ', and " characters
# - Test empty string and very long string edge cases
# Properties to check:
# - & < > should always be converted to &amp; &lt; &gt; 
# - ' and " should only be converted when quote=True
# - Output should be valid HTML that renders the same as the input
@given(st.text())
def test_html_escape(s):
    escaped = html.escape(s)
    assert '&' not in escaped
    assert '<' not in escaped
    assert '>' not in escaped
    assert escaped.count('&amp;') == s.count('&')  
    assert escaped.count('&lt;') == s.count('<')
    assert escaped.count('&gt;') == s.count('>')

    escaped_quotes = html.escape(s, quote=True)
    assert '"' not in escaped_quotes
    assert "'" not in escaped_quotes
    assert escaped_quotes.count('&quot;') == s.count('"')
    assert escaped_quotes.count('&#x27;') == s.count("'")
        
    # Check that output renders the same as input in HTML
    assert s == html.unescape(escaped)
    assert s == html.unescape(escaped_quotes)
# End program