from hypothesis import given, strategies as st
import html

# Summary: Using @given(st.data()), draw a random Unicode string from an alphabet
# that mixes the special HTML characters (&, <, >, ", ') with arbitrary unicode so
# special chars occur frequently, and draw a random `quote` boolean. This covers
# empty strings, normal text, special-char-heavy text, and unicode edge cases.
@given(st.data())
def test_html_escape(data):
    special = ["&", "<", ">", '"', "'"]
    alphabet = st.one_of(st.sampled_from(special), st.characters())

    s = data.draw(st.text(alphabet=alphabet))
    quote = data.draw(st.booleans())

    result = html.escape(s, quote)

    # Output is always a string
    assert isinstance(result, str)

    # Reference escaping: '&' replaced first to avoid double-escaping
    expected = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    if quote:
        expected = expected.replace('"', "&quot;").replace("'", "&#x27;")

    # Exact correctness of substitutions
    assert result == expected

    # '<' and '>' are always escaped, never raw in output
    assert "<" not in result and ">" not in result

    # Conditional quote escaping behavior
    if quote:
        assert '"' not in result and "'" not in result
    else:
        assert result.count('"') == s.count('"')
        assert result.count("'") == s.count("'")
# End program