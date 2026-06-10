from hypothesis import given, strategies as st
import html

# Property 1: Idempotence on plain text (strings without '&' contain no references)
@given(st.text().filter(lambda s: "&" not in s))
def test_html_unescape_no_references_unchanged(s):
    assert html.unescape(s) == s
# End program

# Property 2: Output type and length bound
@given(st.text(max_size=1000))
def test_html_unescape_output_type_and_length(s):
    result = html.unescape(s)
    assert isinstance(result, str)
    assert len(result) <= len(s)
# End program

# Property 3: Correct named reference resolution
@given(st.sampled_from([
    ("&amp;", "&"),
    ("&lt;", "<"),
    ("&gt;", ">"),
    ("&quot;", '"'),
    ("&apos;", "'"),
    ("&copy;", "\u00a9"),
    ("&nbsp;", "\u00a0"),
    ("&euro;", "\u20ac"),
]))
def test_html_unescape_named_references(pair):
    reference, expected = pair
    assert html.unescape(reference) == expected
# End program

# Property 4: Correct numeric reference resolution (decimal and hex agree)
@given(st.integers(min_value=1, max_value=0x10FFFF).filter(
    lambda n: not (0xD800 <= n <= 0xDFFF)))
def test_html_unescape_numeric_references(code_point):
    decimal_ref = f"&#{code_point};"
    hex_lower_ref = f"&#x{code_point:x};"
    hex_upper_ref = f"&#X{code_point:X};"
    dec_result = html.unescape(decimal_ref)
    hex_lower_result = html.unescape(hex_lower_ref)
    hex_upper_result = html.unescape(hex_upper_ref)
    assert dec_result == hex_lower_result == hex_upper_result
# End program

# Property 5: Round-trip consistency with html.escape
@given(st.text(max_size=1000))
def test_html_unescape_roundtrip_with_escape(s):
    assert html.unescape(html.escape(s)) == s
# End program