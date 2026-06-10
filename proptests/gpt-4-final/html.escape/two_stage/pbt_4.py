from hypothesis import given, strategies as st
import html

@given(st.text())
def test_html_escape_ampersand_greater_less(input_string):
    output_string = html.escape(input_string)
    assert '&' not in output_string
    assert '<' not in output_string
    assert '>' not in output_string

@given(st.text(), st.booleans())
def test_html_escape_quote(input_string, quote):
    output_string = html.escape(input_string, quote)
    if quote:
        assert '"' not in output_string
        assert '\'' not in output_string

@given(st.text())
def test_html_escape_length(input_string):
    output_string = html.escape(input_string)
    assert len(output_string) >= len(input_string)

@given(st.text(), st.booleans())
def test_html_escape_bidirectional(input_string, quote):
    escaped_string = html.escape(input_string, quote)
    assert html.unescape(escaped_string) == input_string

@given(st.just(''))
def test_html_escape_empty_string(input_string):
    output_string = html.escape(input_string)
    assert output_string == ''
# End program