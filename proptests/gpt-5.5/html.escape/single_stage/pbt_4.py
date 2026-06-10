from hypothesis import given, strategies as st
import html

# Summary: Generate arbitrary Unicode text, explicit edge-case strings, and strings built from fragments rich in escapable characters (&, <, >, ", '), plus both quote=True and quote=False; check that html.escape performs exactly the documented replacements.
@given(st.data())
def test_html_escape(data):
    special_fragments = st.sampled_from([
        "",
        "&",
        "<",
        ">",
        '"',
        "'",
        "&&",
        "<<>>",
        "<a href=\"x&y\">",
        "Tom & Jerry",
        "already &amp; escaped",
        "emoji 😀 & <tag>",
        "\n\t<&>\"'",
    ])

    s = data.draw(
        st.one_of(
            st.text(),
            special_fragments,
            st.lists(
                st.one_of(st.text(max_size=5), special_fragments),
                min_size=0,
                max_size=20,
            ).map("".join),
        ),
        label="s",
    )
    quote = data.draw(st.booleans(), label="quote")

    expected = (
        s.replace("&", "&amp;")
         .replace("<", "&lt;")
         .replace(">", "&gt;")
    )
    if quote:
        expected = expected.replace('"', "&quot;").replace("'", "&#x27;")

    escaped = html.escape(s, quote=quote)

    assert escaped == expected
    assert "<" not in escaped
    assert ">" not in escaped

    if quote:
        assert '"' not in escaped
        assert "'" not in escaped
    else:
        assert escaped.count('"') == s.count('"')
        assert escaped.count("'") == s.count("'")
# End program