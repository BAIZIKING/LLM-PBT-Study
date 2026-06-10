from hypothesis import given, strategies as st
import html

@given(st.text())
def test_no_named_character_references(s):
    unescaped = html.unescape(s)
    assert "&gt;" not in unescaped
    assert "&amp;" not in unescaped
    assert "&quot;" not in unescaped

@given(st.text())
def test_no_decimal_numeric_character_references(s):
    unescaped = html.unescape(s)
    assert "&#62;" not in unescaped
    assert "&#38;" not in unescaped
    assert "&#34;" not in unescaped

@given(st.text())
def test_no_hexadecimal_numeric_character_references(s):
    unescaped = html.unescape(s)
    assert "&#x3e;" not in unescaped
    assert "&#x26;" not in unescaped
    assert "&#x22;" not in unescaped

@given(st.text())
def test_output_length(s):
    unescaped = html.unescape(s)
    assert len(unescaped) >= len(s)

@given(st.text())
def test_no_character_references_unchanged(s):
    assume(not any(c in s for c in "&<>\"'"))
    unescaped = html.unescape(s)
    assert unescaped == s
# End program