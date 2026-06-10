from hypothesis import given, strategies as st
import html

# Summary: Generate strings by concatenating edge-case segments with known outcomes: arbitrary Unicode text without '&' (must remain unchanged), known HTML5 named references, valid decimal/hex numeric references for safe Unicode characters, malformed references that should remain unchanged, and selected invalid numeric references with documented HTML5 replacement behavior. The property checks exact conversion and that the result is always a string.
@given(st.data())
def test_html_unescape(data):
    safe_unicode_char = st.characters(
        whitelist_categories=(
            "Lu", "Ll", "Lt", "Lm", "Lo",
            "Mn", "Mc", "Me",
            "Nd", "Nl", "No",
            "Pc", "Pd", "Ps", "Pe", "Pi", "Pf", "Po",
            "Sm", "Sc", "Sk", "So",
            "Zs", "Zl", "Zp",
        )
    )

    plain_text = st.text(
        alphabet=safe_unicode_char.filter(lambda c: c != "&"),
        max_size=20,
    ).map(lambda s: (s, s))

    named_reference = st.sampled_from([
        ("&lt;", "<"),
        ("&gt;", ">"),
        ("&amp;", "&"),
        ("&quot;", '"'),
        ("&apos;", "'"),
        ("&nbsp;", "\xa0"),
        ("&copy;", "©"),
        ("&reg;", "®"),
        ("&euro;", "€"),
        ("&NotEqual;", "≠"),
    ])

    valid_decimal_reference = safe_unicode_char.map(
        lambda c: (f"&#{ord(c)};", c)
    )

    valid_hex_reference = safe_unicode_char.flatmap(
        lambda c: st.sampled_from([
            (f"&#x{ord(c):x};", c),
            (f"&#X{ord(c):X};", c),
            (f"&#x{ord(c):04x};", c),
        ])
    )

    malformed_reference = st.sampled_from([
        ("&;", "&;"),
        ("&#;", "&#;"),
        ("&#x;", "&#x;"),
        ("&#X;", "&#X;"),
        ("&#xG;", "&#xG;"),
        ("& #62;", "& #62;"),
        (" & ", " & "),
    ])

    invalid_numeric_reference = st.sampled_from([
        ("&#0;", "\ufffd"),
        ("&#x0;", "\ufffd"),
        ("&#128;", "€"),
        ("&#x80;", "€"),
        ("&#xD800;", "\ufffd"),
        ("&#1114112;", "\ufffd"),
    ])

    segment = st.one_of(
        plain_text,
        named_reference,
        valid_decimal_reference,
        valid_hex_reference,
        malformed_reference,
        invalid_numeric_reference,
    )

    segments = data.draw(st.lists(segment, min_size=0, max_size=50))

    s = "".join(source for source, _ in segments)
    expected = "".join(value for _, value in segments)

    result = html.unescape(s)

    assert isinstance(result, str)
    assert result == expected
# End program