from hypothesis import given, strategies as st
import html

# Property Idempotence
@given(st.text())
def test_idempotence(text):
    assert html.unescape(html.unescape(text)) == html.unescape(text)

# Property of Retained Length
@given(st.text())
def test_retained_length(text):
    assert len(html.unescape(text)) <= len(text)

# No Escaping Sequences
@given(st.text())
def test_no_escaping_sequence(text):
    unescaped = html.unescape(text)
    assert '&' not in unescaped and ';' not in unescaped

# Property of Reversible Operation
@given(st.text())
def test_reversible_operation(text):
    assert html.escape(html.unescape(text)) == text

# Special Characters Handling
@given(st.text())
def test_special_chars_handling(text):
    unescaped = html.unescape(text)
    assert all(char in unescaped for char in text if not (char == '&' or char == ';'))