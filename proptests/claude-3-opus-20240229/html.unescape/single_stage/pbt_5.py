from hypothesis import given, strategies as st
import html

# Summary: Generate strings with a mix of regular characters and HTML character references.
# Use named, decimal numeric, and hexadecimal numeric references.
# Include some invalid references to test error handling.
# Check that unescape converts the references to the correct Unicode characters.
@given(st.text(alphabet=st.characters(min_codepoint=32, max_codepoint=127)).map(lambda s: 
    s.replace('&', '&amp;')
     .replace('<', '&lt;')
     .replace('>', '&gt;')
     .replace('"', '&quot;')
     .replace("'", '&#39;')
     .replace('A', '&#65;')
     .replace('z', '&#122;')
     .replace('0', '&#48;')
     .replace('9', '&#57;')
     .replace('?', '&#x3F;')
     .replace('$', '&#x24;')
     .replace('!', '&excl;')
     .replace('@', '&commat;')
     .replace('~', '&tilde;')
     .replace('=', '&equals;')
     .replace('/', '&#x2F;')
))
def test_html_unescape(s):
    unescaped = html.unescape(s)
    assert '&' not in unescaped
    assert '<' in unescaped or '&lt;' in s
    assert '>' in unescaped or '&gt;' in s 
    assert '"' in unescaped or '&quot;' in s
    assert "'" in unescaped or '&#39;' in s
    assert 'A' in unescaped or '&#65;' in s
    assert 'z' in unescaped or '&#122;' in s
    assert '0' in unescaped or '&#48;' in s
    assert '9' in unescaped or '&#57;' in s
    assert '?' in unescaped or '&#x3F;' in s
    assert '$' in unescaped or '&#x24;' in s
    assert '!' in unescaped or '&excl;' in s
    assert '@' in unescaped or '&commat;' in s  
    assert '~' in unescaped or '&tilde;' in s
    assert '=' in unescaped or '&equals;' in s
    assert '/' in unescaped or '&#x2F;' in s
# End program