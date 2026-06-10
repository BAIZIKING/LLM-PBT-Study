from hypothesis import given, strategies as st
import html

# Summary: The generation strategy aims to create a diverse set of inputs for html.escape, including:
# 1. Random strings with varying lengths and character compositions.
# 2. Strings specifically containing HTML special characters (&, <, >, ", ').
# 3. Edge cases such as empty strings and None.
@given(st.data())
def test_html_escape(data):
    # Generate random strings, including those with special HTML characters.
    random_string = data.draw(st.text(alphabet=st.characters(blacklist_categories=('C'))))
    
    # Generate strings with HTML special characters.
    special_chars_string = data.draw(
        st.text(alphabet=st.characters(min_codepoint=32, max_codepoint=126) | st.sampled_from(['&', '<', '>', '"', "'"]))
    )
    
    # Test with both quote=True and quote=False.
    for quote_flag in [True, False]:
        escaped_string = html.escape(random_string, quote=quote_flag)
        escaped_special_chars_string = html.escape(special_chars_string, quote=quote_flag)

        # Property 1: Check if the escaped string no longer contains the raw special HTML characters.
        for char in '&<>"':
            if quote_flag or char in '&<>':
                assert char not in escaped_string
                assert char not in escaped_special_chars_string

        # Property 2: Check if escaping an already escaped string doesn't double escape.
        double_escaped_string = html.escape(escaped_string, quote=quote_flag)
        assert double_escaped_string == escaped_string

        # Property 3 (Edge case): Check if escaping an empty string or None returns an empty string.
        assert html.escape("", quote=quote_flag) == ""
        assert html.escape(None, quote=quote_flag) == ""
# End program