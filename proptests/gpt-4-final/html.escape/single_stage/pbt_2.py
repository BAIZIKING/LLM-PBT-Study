from hypothesis import given, strategies as st

# Summary: This test generates a random string and a random boolean value to use as inputs for html.escape. It then checks that the output of html.escape does not contain &, <, and > characters, and if quote=True, does not contain " and ' characters.
@given(st.text(), st.booleans())
def test_html_escape(input_string, quote):
    escaped_string = html.escape(input_string, quote)
    
    assert '&' not in escaped_string
    assert '<' not in escaped_string
    assert '>' not in escaped_string
    
    if quote:
        assert '"' not in escaped_string
        assert '\'' not in escaped_string
# End program