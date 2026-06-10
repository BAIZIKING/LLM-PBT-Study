from hypothesis import given, strategies as st
import html

@given(st.text())
def test_html_escape_ampersand(text):
    escaped_text = html.escape(text)
    assert escaped_text.find('&') == -1

@given(st.text())
def test_html_escape_angle_brackets(text):
    escaped_text = html.escape(text)
    assert escaped_text.find('<') == -1
    assert escaped_text.find('>') == -1

@given(st.text())
def test_html_escape_quotes(text):
    escaped_text = html.escape(text, quote=True)
    assert escaped_text.find('"') == -1
    assert escaped_text.find("'") == -1

@given(st.text())
def test_html_escape_length(text):
    escaped_text = html.escape(text)
    assert len(escaped_text) >= len(text)

@given(st.text())
def test_html_escape_type(text):
    escaped_text = html.escape(text)
    assert isinstance(escaped_text, str)