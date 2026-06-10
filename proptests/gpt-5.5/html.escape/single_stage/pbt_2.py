from hypothesis import given, strategies as st
import html

# Summary: Generate quote as a boolean and s as either empty text, arbitrary Unicode text, or strings built from edge-case tokens including &, <, >, both quotes, whitespace, NUL, existing-looking entities, and non-ASCII characters; check that html.escape performs exactly the documented replacements, preserving quotes only when quote=False.
@given(st.data())
def test_html_escape(data):
    s = data.draw(
        st.one_of(
            st.just(""),
            st.text(),
            st.lists(
                st.sampled_from([
                    "&", "<", ">", '"', "'", " ",
                    "\n", "\t", "\x00",
                    "&amp;", "&lt;", "&gt;", "&quot;", "&#x27;",
                    "abc", "é", "中", "😀",
                ]),
                min_size=0,
                max_size=100,
            ).map("".join),
        ),
        label="s",
    )
    quote = data.draw(st.booleans(), label="quote")

    expected = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    if quote:
        expected = expected.replace('"', "&quot;").replace("'", "&#x27;")

    actual = html.escape(s, quote=quote)

    assert actual == expected
    assert "<" not in actual
    assert ">" not in actual
    if quote:
        assert '"' not in actual
        assert "'" not in actual
    else:
        assert actual.count('"') == s.count('"')
        assert actual.count("'") == s.count("'")
# End program