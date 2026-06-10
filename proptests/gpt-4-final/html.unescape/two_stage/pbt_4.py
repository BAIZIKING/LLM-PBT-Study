from hypothesis import given, strategies as st
import html

@given(s=st.text())
def test_idempotency(s):
    assert html.unescape(html.unescape(s)) == html.unescape(s)

@given(s=st.text())
def test_reversibility(s):
    assert html.escape(html.unescape(s)) == s

@given(s=st.text())
def test_characters_conservation(s):
    assert len(html.unescape(s)) >= len(s)

@given(s=st.text())
def test_size_expectation(s):
    if '&' in s:
        assert len(html.unescape(s)) <= len(s)

@given(s=st.text())
def test_character_type(s):
    unescaped = html.unescape(s)
    assert "&" not in unescaped or unescaped.find('&') > unescaped.find(';')  # ignoring & in normal text
# End program