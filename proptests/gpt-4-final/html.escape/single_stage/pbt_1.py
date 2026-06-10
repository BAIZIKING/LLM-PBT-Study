from hypothesis import given, strategies as st
import html

# Utilize st.text() to generate wide variety of inputs and edge cases
@given(st.text())
def test_html_escape(text):
    # Generate the escaped text
    escaped_text = html.escape(text)

    # Ensure there are no &, <, >, " or ' characters in the output
    assert "&" not in escaped_text
    assert "<" not in escaped_text
    assert ">" not in escaped_text
    assert "\"" not in escaped_text
    assert "\'" not in escaped_text
    
    # Ensure the output length is greater or equal to input length
    assert len(escaped_text) >= len(text)
# End program