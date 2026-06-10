from hypothesis import given, strategies as st
import html

@given(st.text())
def test_no_named_references(s):
    unescaped = html.unescape(s)
    assert "&" not in unescaped or ";" not in unescaped

@given(st.text())
def test_no_decimal_numeric_references(s):
    unescaped = html.unescape(s)
    assert "&#" not in unescaped or ";" not in unescaped

@given(st.text())
def test_no_hexadecimal_numeric_references(s):
    unescaped = html.unescape(s)
    assert "&#x" not in unescaped or ";" not in unescaped

@given(st.text())
def test_valid_unicode(s):
    unescaped = html.unescape(s)
    assert isinstance(unescaped, str)

@given(st.text())
def test_output_length(s):
    unescaped = html.unescape(s)
    assert len(unescaped) >= len(s)
# End program