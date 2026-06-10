from hypothesis import given, strategies as st
from html import escape

@given(st.text())
def test_html_escape(test_string):
    # Property 1: Verify all important characters are replaced with their HTML-safe sequences
    escaped_string = escape(test_string)
    for char in ["&", "<", ">", '"', "'"]:
        assert test_string.count(char) == escaped_string.count("&"+str(ord(char))+";")

    # Property 2: Verify there are no important characters left unescaped
    for char in ["&", "<", ">", '"', "'"]:
        assert escaped_string.count(char) == (escaped_string.count("&"+str(ord(char))+";") if char != "&" else escaped_string.count("&")+1)
# End program