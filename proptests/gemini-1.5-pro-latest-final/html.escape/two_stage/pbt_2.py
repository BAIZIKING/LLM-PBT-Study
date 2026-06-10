from hypothesis import given, strategies as st
import html

@given(st.text())
def test_correct_escape_sequences(s):
    escaped = html.escape(s)
    assert '&amp;' in escaped or '&' not in s 
    assert '&lt;' in escaped or '<' not in s
    assert '&gt;' in escaped or '>' not in s
    assert '&quot;' in escaped or '"' not in s
    assert '&#x27;' in escaped or "'" not in s
# End program