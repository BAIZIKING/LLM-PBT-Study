from hypothesis import given, strategies as st
import html
import string

@given(st.text())
def test_no_html_references(s):
    unescaped = html.unescape(s)
    assert "&" not in unescaped or "&#" not in unescaped

@given(st.text())
def test_output_length(s):
    unescaped = html.unescape(s)
    assert len(unescaped) <= len(s)

@given(st.text())
def test_valid_unicode(s):
    unescaped = html.unescape(s)
    assert all(ord(c) <= 0x10FFFF for c in unescaped)

@given(st.text())
def test_output_substring(s):
    unescaped = html.unescape(s)
    assert all(c in s for c in unescaped if c not in string.punctuation)

@given(st.text())
def test_idempotence(s):
    unescaped = html.unescape(s)
    assert html.unescape(unescaped) == unescaped
# End program