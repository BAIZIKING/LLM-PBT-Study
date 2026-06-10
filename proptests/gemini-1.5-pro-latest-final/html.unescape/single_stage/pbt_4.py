from hypothesis import given, strategies as st

# Summary: Generates various strings with and without HTML entities
@given(st.text() | st.sampled_from(["&amp;", "&lt;", "&gt;", "&#62;", "&#x3e;"]) | st.integers().map(lambda x: f"&#{x};") | st.just(""))
def test_html_unescape(s):
    unescaped = html.unescape(s)
    # Check if named and numeric entities are correctly converted
    assert "&" not in unescaped and "<" not in unescaped and ">" not in unescaped 
    # Check if invalid entities are handled (assuming replacement with �)
    assert "�" in unescaped or all(c in unescaped for c in s) 
    # Check if non-entity characters are preserved
    for c in s:
        if c not in "&<>;":
            assert c in unescaped

# End program