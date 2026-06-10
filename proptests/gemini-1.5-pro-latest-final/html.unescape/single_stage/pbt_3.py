from hypothesis import given, strategies as st
from html import unescape

# Summary: Generates strings with ASCII, Unicode, control characters, and various HTML entities (named, numeric, invalid)
@given(st.text(alphabet=st.characters(blacklist_categories=('Cs',)), allow_unicode=True))
def test_html_unescape(s):
    unescaped_string = unescape(s)
    
    # Check for unchanged characters outside of entities
    for i, char in enumerate(unescaped_string):
        if s[i:i+1] not in ('&', ';'):
            assert char == s[i]

    # Check for correct unescaping of known entities
    assert unescape("&amp;") == "&"
    assert unescape("&gt;") == ">"
    assert unescape("&#62;") == ">"
    assert unescape("&#x3e;") == ">"

# End program