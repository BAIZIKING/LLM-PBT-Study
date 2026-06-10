from hypothesis import given, strategies as st
import html

# Summary: Generate random strings using an alphabet rich in HTML special
# characters (&, <, >, ", '), plus normal ASCII and Unicode, including empty
# strings. Also generate a boolean for the `quote` flag. We verify that the
# output is a str, that &/</> are always escaped, that "/' are escaped only
# when quote=True (and untouched when quote=False), and that no raw < or >
# remain in the output. We also verify counts of escaped sequences match the
# counts of the corresponding raw characters in the input.
@given(
    s=st.text(
        alphabet=st.one_of(
            st.sampled_from(['&', '<', '>', '"', "'", ' ', 'a', '1', '\n', '\t', '\u00e9', '\u4e2d']),
            st.characters(),
        ),
    ),
    quote=st.booleans(),
)
def test_html_escape(s, quote):
    result = html.escape(s, quote=quote)

    # Property 1: output is always a string
    assert isinstance(result, str)

    # Property 2-4: &, <, > are always escaped regardless of quote
    # No raw < or > should appear in the output at all.
    assert '<' not in result
    assert '>' not in result

    # Property: counts of escaped sequences match counts of raw chars in input.
    # & is escaped first by html.escape, so each raw & yields exactly one &amp;
    assert result.count('&amp;') == s.count('&')
    # Each raw < / > yields one &lt; / &gt;
    assert result.count('&lt;') == s.count('<')
    assert result.count('&gt;') == s.count('>')

    if quote:
        # Property 5: when quoting, " and ' are escaped
        assert '"' not in result
        # html escapes " to &quot; and ' to &#x27;
        assert result.count('&quot;') == s.count('"')
        assert result.count('&#x27;') == s.count("'")
    else:
        # Property 6: when not quoting, " and ' pass through unchanged
        assert result.count('"') == s.count('"')
        assert result.count("'") == s.count("'")

    # Property 7 (round-trip): unescaping should recover the original string,
    # since escaping is a faithful, reversible encoding of these characters.
    assert html.unescape(result) == s
# End program