from hypothesis import given, strategies as st
import html
import string

@given(st.text(alphabet=st.characters(blacklist_categories=('Cc', 'Cs')))) 
def test_preserves_alphanumeric(s):
    # Blacklist control and surrogate characters to avoid potential encoding issues
    escaped = html.escape(s)
    for char in s:
        assert char in escaped
# End program