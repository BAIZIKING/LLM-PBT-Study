from hypothesis import given, strategies as st
import html
import re

@given(st.text(), st.booleans())
def test_no_reserved_html_characters(s, quote):
    result = html.escape(s, quote)
    if quote:
        assert re.search(r'[&<>\'"]', result) is None
    else:
        assert re.search(r'[&<>]', result) is None

@given(st.text(), st.booleans())
def test_length_of_output(s, quote):
    result = html.escape(s, quote)
    assert len(result) >= len(s)

@given(st.text(), st.booleans())
def test_idempotence(s, quote):
    result = html.escape(s, quote)
    assert html.escape(result, quote) == result

@given(st.text(), st.booleans())
def test_correct_translation_of_characters(s, quote):
    result = html.escape(s, quote)
    for i, o in [("&", "&amp;"), ("<", "&lt;"), (">", "&gt;"), ("\"", "&quot;"), ("'", "&#x27;")]:
        if i in s and (not (i in ['"', "'"]) or quote):
            assert s.count(i) == result.count(o)

@given(st.booleans())
def test_output_on_empty_string(quote):
    s = ''
    result = html.escape(s, quote)
    assert result == ''
# End program