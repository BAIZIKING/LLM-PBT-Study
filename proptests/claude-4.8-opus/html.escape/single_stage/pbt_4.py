from hypothesis import given, strategies as st
import html

# Summary: Generate strings from an alphabet that emphasizes the special characters
# (&, <, >, ", ') mixed with arbitrary Unicode characters, plus a boolean quote flag,
# ensuring frequent special-char occurrences alongside general text and empty strings.
@given(st.data())
def test_html_escape(data):
    special = '&<>"\''
    s = data.draw(
        st.text(alphabet=st.one_of(st.sampled_from(special), st.characters()))
    )
    quote = data.draw(st.booleans())

    result = html.escape(s, quote)

    # & is always escaped; no raw <, > remain
    assert '<' not in result
    assert '>' not in result
    assert result.count('&lt;') == s.count('<')
    assert result.count('&gt;') == s.count('>')

    if quote:
        # quotes are escaped, so no raw quote chars remain
        assert '"' not in result
        assert "'" not in result
        assert result.count('&quot;') == s.count('"')
        assert result.count('&#x27;') == s.count("'")
    else:
        # quotes are left untouched
        assert result.count('"') == s.count('"')
        assert result.count("'") == s.count("'")
# End program