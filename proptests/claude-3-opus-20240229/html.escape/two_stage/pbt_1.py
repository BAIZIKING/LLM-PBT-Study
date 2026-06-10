from hypothesis import given, strategies as st
import html

@given(st.text())
def test_no_unescaped_chars(s):
    escaped = html.escape(s)
    assert '&' not in escaped or '&amp;' in escaped
    assert '<' not in escaped or '&lt;' in escaped
    assert '>' not in escaped or '&gt;' in escaped

@given(st.text(), st.booleans())
def test_quote_escaping(s, quote):
    escaped = html.escape(s, quote=quote)
    if quote:
        assert '"' not in escaped or '&quot;' in escaped
        assert "'" not in escaped or '&#x27;' in escaped

@given(st.text())
def test_output_length(s):
    escaped = html.escape(s)
    assert len(escaped) >= len(s)

@given(st.text())
def test_idempotence(s):
    escaped = html.escape(s)
    assert html.escape(escaped) == escaped

@given(st.text())
def test_no_escape_needed(s):
    assume(all(c not in s for c in '&<>"\''))
    assert html.escape(s) == s
# End program