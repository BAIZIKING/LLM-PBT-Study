from hypothesis import given, strategies as st
import html

@given(st.text())
def test_no_character_references(s):
    unescaped = html.unescape(s)
    assert '&' not in unescaped or ';' not in unescaped

@given(st.text())
def test_output_length(s):
    unescaped = html.unescape(s)
    assert len(unescaped) >= len(s)

@given(st.text())
def test_valid_characters(s):
    unescaped = html.unescape(s)
    assert all(ord(c) < 0x110000 for c in unescaped)

@given(st.text())
def test_escape_unescape_roundtrip(s):
    assert html.unescape(html.escape(s)) == s

@given(st.just(''))
def test_empty_string(s):
    assert html.unescape(s) == ''
# End program