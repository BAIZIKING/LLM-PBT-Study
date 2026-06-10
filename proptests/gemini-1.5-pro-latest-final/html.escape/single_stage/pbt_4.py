from hypothesis import given, strategies as st

# Summary: Generates strings with diverse characters and lengths, and varies the quote flag.
@given(st.text(alphabet=st.characters(blacklist_categories=('C'))), st.booleans())
def test_html_escape(s, quote):
    escaped = html.escape(s, quote=quote)
    # Check escaping of &, <, and >
    assert "&" not in escaped
    assert "<" not in escaped
    assert ">" not in escaped
    # Check optional escaping of " and '
    if quote:
        assert '"' not in escaped
        assert "'" not in escaped
    # Check for unchanged characters
    for char in s:
        if char not in "&<>\"'":
            assert char in escaped
# End program