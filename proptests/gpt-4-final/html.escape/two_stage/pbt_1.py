from hypothesis import given, strategies as st
import html

@given(st.text())
def test_no_html_unsafe_characters(s):
    result = html.escape(s)
    assert not any(c in result for c in '&<>')

@given(st.text(), st.booleans())
def test_no_quotation_marks(s, quote):
    result = html.escape(s, quote=quote)
    if quote:
        assert '"' not in result and "'" not in result
    else:
        assert '"' in result or "'" in result or result == ''

@given(st.text(), st.booleans())
def test_non_html_special_characters_remain_same(s, quote):
    result = html.escape(s, quote=quote)
    assert all(c == r for c, r in zip(s, result) if c not in '&<>"\'')

@given(st.booleans())
def test_empty_string_returns_empty_string(quote):
    result = html.escape('', quote=quote)
    assert result == ''