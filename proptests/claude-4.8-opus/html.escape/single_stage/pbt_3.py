from hypothesis import given, strategies as st
import html

# Summary: Generate strings from an alphabet that heavily weights the special
# characters (&, <, >, ", ') mixed with arbitrary Unicode text and edge cases
# (empty, special-only), plus a random `quote` boolean. Verify against a
# reference implementation applying the documented replacements in order, and
# check that no raw special characters that should be escaped remain.
@given(st.data())
def test_html_escape():
    specials = st.text(alphabet="&<>\"'", min_size=0, max_size=10)
    mixed = st.text(min_size=0, max_size=50)
    s = st.data().conjecture_data  # placeholder, replaced below
    s = None

    # Draw the actual inputs
    data = st.data
    # Build the string by interleaving special-heavy and general text
    parts = []

@given(s=st.text(alphabet=st.characters(), min_size=0, max_size=80)
       | st.text(alphabet="&<>\"'abc <>& ", min_size=0, max_size=40),
       quote=st.booleans())
def test_html_escape(s, quote):
    result = html.escape(s, quote)

    # Reference implementation following the documented replacement order:
    # & must be replaced first to avoid double-escaping the entities.
    expected = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    if quote:
        expected = expected.replace('"', "&quot;").replace("'", "&#x27;")

    # Property 1: matches the documented behavior exactly.
    assert result == expected

    # Property 2: raw < and > never survive in the output.
    assert "<" not in result
    assert ">" not in result

    # Property 3: when quote=True, raw " and ' never survive either.
    if quote:
        assert '"' not in result
        assert "'" not in result

    # Property 4: a string with no special characters is returned unchanged.
    if not any(c in s for c in ("&", "<", ">") + (('"', "'") if quote else ())):
        assert result == s
# End program