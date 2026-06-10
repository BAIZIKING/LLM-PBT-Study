from hypothesis import given, strategies as st
import html
import string

@given(st.text())
def test_no_unsafe_characters(s):
    escaped = html.escape(s)
    assert '&' not in escaped or '&amp;' in escaped
    assert '<' not in escaped or '&lt;' in escaped
    assert '>' not in escaped or '&gt;' in escaped

@given(st.text(), st.booleans())
def test_quote_handling(s, quote):
    escaped = html.escape(s, quote=quote)
    if quote:
        assert '"' not in escaped or '&quot;' in escaped
        assert "'" not in escaped or '&#x27;' in escaped

@given(st.text(max_size=1000))
def test_output_length(s):
    escaped = html.escape(s)
    assert len(escaped) >= len(s)

@given(st.text(alphabet=string.ascii_letters + string.digits + string.punctuation))
def test_safe_characters_unchanged(s):
    escaped = html.escape(s)
    for char in s:
        if char not in '&<>"\'':
            assert char in escaped

@given(st.text(max_size=1000))
def test_idempotence(s):
    escaped = html.escape(s)
    assert html.escape(escaped) == escaped
# End program