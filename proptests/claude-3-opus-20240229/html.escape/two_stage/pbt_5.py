from hypothesis import given, strategies as st
import html

@given(st.text())
def test_escape_special_characters(s):
    escaped = html.escape(s)
    assert '&' not in escaped or '&amp;' in escaped
    assert '<' not in escaped or '&lt;' in escaped
    assert '>' not in escaped or '&gt;' in escaped

@given(st.text(), st.booleans())
def test_escape_quotes(s, quote):
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
def test_no_escaping_needed(s):
    if not any(c in s for c in ['&', '<', '>', '"', "'"]):
        assert html.escape(s) == s
# End program