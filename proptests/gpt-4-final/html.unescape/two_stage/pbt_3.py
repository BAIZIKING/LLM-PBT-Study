from hypothesis import given, strategies as st
import html

# Test 1: Identity
@given(st.text())
def test_html_unescape_identity(s):
    if all(c not in s for c in ["&", "<", ">", "\"", "\'"]):
        assert html.unescape(s) == s

# Test 2: Output Type
@given(st.text())
def test_html_unescape_output_type(s):
    assert isinstance(html.unescape(s), str)

# Test 3: Unicode Conversion
@given(st.text(st.characters(blacklist_categories=('Cc', 'Cs', 'Mc', 'Me', 'Mn', 'Zs', 'Zl', 'Zp'))))
def test_html_unescape_unicode_conversion(s):
    unescaped_str = html.unescape(s)
    if "&" in s:
        assert "&" not in unescaped_str and ";" not in unescaped_str

# Test 4: Length Inequality
@given(st.text(st.characters(blacklist_categories=('Cc', 'Cs', 'Mc', 'Me', 'Mn', 'Zs', 'Zl', 'Zp'))))
def test_html_unescape_length_inequality(s):
    unescaped_str = html.unescape(s)
    if "&" in s and ";" in s:
        assert len(unescaped_str) <= len(s)

# Test 5: HTML 5 Compliant
@given(st.text(st.characters(blacklist_categories=('Cc', 'Cs', 'Mc', 'Me', 'Mn', 'Zs', 'Zl', 'Zp'))))
def test_html_unescape_html5_compliant(s):
    unescaped_str = html.unescape(s)
    if "&" in s and ";" in s:
        assert "&" not in unescaped_str and ";" not in unescaped_str

# End program