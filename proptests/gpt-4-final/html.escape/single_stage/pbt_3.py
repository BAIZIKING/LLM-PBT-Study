from hypothesis import given, strategies as st
from html import escape

@given(st.text(st.characters(whitelist_categories=('Pc', 'Pd', 'Pe', 'Pf', 'Pi', 'Po', 'Ps', 'Cc', 'Cf', 'Co', 'Cs', '&', '<', '>', '"', "'"))))
def test_html_escape(string: str) -> None:
    escaped_string_no_quotes = escape(string, quote=False)
    assert '&' not in escaped_string_no_quotes
    assert '<' not in escaped_string_no_quotes
    assert '>' not in escaped_string_no_quotes
    assert '"' in escaped_string_no_quotes
    assert "'" in escaped_string_no_quotes
    
    escaped_string_with_quotes = escape(string, quote=True)
    assert '&' not in escaped_string_with_quotes
    assert '<' not in escaped_string_with_quotes
    assert '>' not in escaped_string_with_quotes
    assert '"' not in escaped_string_with_quotes
    assert "'" not in escaped_string_with_quotes
# End program