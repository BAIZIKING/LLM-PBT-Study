from hypothesis import given, strategies as st
import html

_named_references = tuple(html.entities.html5.items())

_no_ampersand_text = st.text(
    alphabet=st.characters(blacklist_characters="&"),
    max_size=1000,
)

_valid_codepoints = st.integers(min_value=0, max_value=0x10FFFF)

_invalid_or_disallowed_codepoints = st.one_of(
    st.integers(min_value=0xD800, max_value=0xDFFF),
    st.integers(min_value=0x110000, max_value=0x120000),
)


@given(st.text(max_size=1000))
def test_html_unescape_output_is_str(s):
    result = html.unescape(s)
    assert isinstance(result, str)


@given(_no_ampersand_text)
def test_html_unescape_preserves_text_without_character_references(s):
    result = html.unescape(s)
    assert result == s


@given(_valid_codepoints)
def test_html_unescape_decimal_and_hex_numeric_references_agree(codepoint):
    decimal_reference = f"&#{codepoint};"
    hexadecimal_reference = f"&#x{codepoint:x};"

    decimal_result = html.unescape(decimal_reference)
    hexadecimal_result = html.unescape(hexadecimal_reference)

    assert decimal_result == hexadecimal_result


@given(st.sampled_from(_named_references))
def test_html_unescape_named_character_references_are_replaced(named_reference):
    name, expected_value = named_reference

    result = html.unescape(f"&{name}")

    assert result == expected_value


@given(_invalid_or_disallowed_codepoints)
def test_html_unescape_invalid_or_disallowed_numeric_references_use_replacement_character(codepoint):
    result = html.unescape(f"&#{codepoint};")

    assert result == "\ufffd"
# End program