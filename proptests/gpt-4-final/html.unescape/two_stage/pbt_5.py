from hypothesis import given, strategies as st
import html

# Property 1: Idempotency
@given(st.text())
def test_idempotency(input_string):
    assert html.unescape(html.unescape(input_string)) == html.unescape(input_string)

# Property 2: Length Preservation
@given(st.text())
def test_length_preservation(input_string):
    unescaped = html.unescape(input_string)
    assert len(input_string) >= len(unescaped)

# Property 3: Consistency
@given(st.text())
def test_consistency(input_string):
    unescaped = html.unescape(input_string)
    assert unescaped == html.unescape(unescaped)

# Property 4: HTML Encoding
@given(st.text())
def test_html_encoding(input_string):
    unescaped = html.unescape(input_string)
    assert "&" not in unescaped

# Property 5: Unicode Characters
@given(st.text())
def test_unicode_characters(input_string):
    unescaped = html.unescape(input_string)
    for character in unescaped:
        assert ord(character) < 0x110000
# End program