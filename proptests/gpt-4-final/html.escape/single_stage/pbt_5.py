from hypothesis import given, strategies as st
import html

@given(st.text())
def test_html_escape(input_str):
    escaped_str = html.escape(input_str)
    
    # Ensure the output does not contain the special characters
    special_chars = ["&", "<", ">", "\"", "'"]
    assert not any(char in escaped_str for char in special_chars)

    # Ensure html.escape does not change the original string except the special characters
    for char in escaped_str:
        if char not in special_chars:
            assert char in input_str
# End program