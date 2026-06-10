from hypothesis import given, strategies as st
import html

# Summary: The generation strategy aims to create a diverse set of inputs for `html.escape` by considering various data types, edge cases, and potential HTML-sensitive characters.
@given(st.data())
def test_html_escape(data):
    # Generate strings with varying lengths and characters, including special HTML characters.
    input_string = data.draw(
        st.text(
            alphabet=st.characters(
                min_codepoint=1, max_codepoint=127, blacklist_categories=("Cc", "Cs")
            ),
            min_size=0,
            max_size=100,
        )
    )

    # Generate boolean values to test the optional `quote` parameter.
    quote_flag = data.draw(st.booleans())

    # Escape the input string using `html.escape`.
    escaped_string = html.escape(input_string, quote=quote_flag)

    # Check if the escaped string contains any of the original special HTML characters.
    assert "&" not in escaped_string
    assert "<" not in escaped_string
    assert ">" not in escaped_string

    # If the `quote` flag is True, check if quotes are also escaped.
    if quote_flag:
        assert '"' not in escaped_string
        assert "'" not in escaped_string

# End program