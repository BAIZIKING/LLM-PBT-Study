from hypothesis import given, strategies as st
import html

# Summary: The generation strategy aims to create a diverse set of inputs for `html.escape` by considering various data types, lengths, and special characters. 
# This includes strings with alphanumeric characters, empty strings, strings with only special HTML characters, and strings with a mix of alphanumeric and special characters.
@given(st.text(alphabet=st.characters(blacklist_categories=('C', 'Cs'))))
def test_html_escape(s):
    escaped_string = html.escape(s)
    # Property 1: Check if the escaped string only contains alphanumeric characters, spaces, and the escaped versions of special HTML characters (&, <, >, ", ').
    assert all(c.isalnum() or c in " &#<>'\"" for c in escaped_string)
    # Property 2: Verify that the length of the escaped string is always greater than or equal to the original string, as escaping characters can only increase the length.
    assert len(escaped_string) >= len(s)
# End program