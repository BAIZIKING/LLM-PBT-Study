from hypothesis import given, strategies as st
import html

@given(st.text())
def test_idempotence(s):
    once_escaped = html.escape(s)
    twice_escaped = html.escape(once_escaped)
    assert once_escaped == twice_escaped 
# End program