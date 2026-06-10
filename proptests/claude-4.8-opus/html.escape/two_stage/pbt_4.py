from hypothesis import given, strategies as st
import html
import re


@given(s=st.text(max_size=1000))
def test_html_escape_no_raw_ampersand(s):
    # Property 1: every '&' in the output is the start of a valid HTML escape sequence
    for quote in (True, False):
        out = html.escape(s, quote=quote)
        # Find all '&' positions and check they begin a known entity
        valid_entities = ("&amp;", "&lt;", "&gt;", "&quot;", "&#x27;")
        i = 0
        while i < len(out):
            if out[i] == "&":
                assert any(out.startswith(ent, i) for ent in valid_entities), \
                    f"Raw or invalid '&' at index {i} in {out!r}"
            i += 1
# End program


@given(s=st.text(max_size=1000))
def test_html_escape_no_raw_angle_brackets(s):
    # Property 2: output never contains raw '<' or '>' for either quote value
    for quote in (True, False):
        out = html.escape(s, quote=quote)
        assert "<" not in out
        assert ">" not in out
# End program


@given(s=st.text(max_size=1000))
def test_html_escape_quote_handling(s):
    # Property 3: quote flag controls escaping of '"' and "'"
    out_quoted = html.escape(s, quote=True)
    assert '"' not in out_quoted
    assert "'" not in out_quoted

    out_unquoted = html.escape(s, quote=False)
    # In unquoted mode, count of raw quotes preserved
    assert out_unquoted.count('"') == s.count('"')
    assert out_unquoted.count("'") == s.count("'")
# End program


@given(
    s=st.text(
        alphabet=st.characters(blacklist_characters="&<>\"'"),
        max_size=1000,
    )
)
def test_html_escape_identity_on_safe_strings(s):
    # Property 4: strings with no special chars are returned unchanged
    assert html.escape(s, quote=True) == s
    assert html.escape(s, quote=False) == s
# End program


@given(s=st.text(max_size=1000))
def test_html_escape_preserves_other_characters(s):
    # Property 5: non-special characters appear unchanged and in same order
    special = set("&<>\"'")
    for quote in (True, False):
        out = html.escape(s, quote=quote)
        input_non_special = [c for c in s if c not in special]

        # Remove all known entity sequences from output, then collect remaining chars
        entities = ("&amp;", "&lt;", "&gt;", "&quot;", "&#x27;")
        pattern = "|".join(re.escape(e) for e in entities)
        stripped = re.sub(pattern, "", out)
        output_non_special = [c for c in stripped if c not in special]

        assert output_non_special == input_non_special
# End program