from hypothesis import given, strategies as st
import html

# Summary: Generate strings as concatenations of plain Unicode text without "&", known HTML5 named references, valid decimal/hex numeric references, and selected HTML5-invalid numeric references with documented replacement behavior; check exact one-pass unescaping.
@given(st.data())
def test_html_unescape(data):
    def is_direct_html5_codepoint(cp):
        return not (
            cp == 0
            or 0x0001 <= cp <= 0x0008
            or 0x000E <= cp <= 0x001F
            or 0x007F <= cp <= 0x009F
            or 0xD800 <= cp <= 0xDFFF
            or 0xFDD0 <= cp <= 0xFDEF
            or (cp & 0xFFFE) == 0xFFFE
        )

    plain_token = st.text(
        alphabet=st.characters(blacklist_characters="&"),
        max_size=20,
    ).map(lambda s: (s, s))

    named_token = st.sampled_from(
        [
            ("&gt;", ">"),
            ("&lt;", "<"),
            ("&amp;", "&"),
            ("&quot;", '"'),
            ("&apos;", "'"),
            ("&nbsp;", "\u00a0"),
            ("&copy;", "\u00a9"),
            ("&reg;", "\u00ae"),
            ("&euro;", "\u20ac"),
        ]
    )

    valid_codepoint = st.integers(min_value=1, max_value=0x10FFFF).filter(
        is_direct_html5_codepoint
    )

    numeric_token = valid_codepoint.flatmap(
        lambda cp: st.sampled_from(
            [
                (f"&#{cp};", chr(cp)),
                (f"&#x{cp:x};", chr(cp)),
                (f"&#X{cp:X};", chr(cp)),
            ]
        )
    )

    invalid_numeric_token = st.sampled_from(
        [
            ("&#0;", "\ufffd"),
            ("&#x0;", "\ufffd"),
            ("&#x80;", "\u20ac"),
            ("&#x81;", ""),
            ("&#xD800;", ""),
            ("&#1114112;", "\ufffd"),
            ("&#x110000;", "\ufffd"),
        ]
    )

    tokens = data.draw(
        st.lists(
            st.one_of(
                plain_token,
                named_token,
                numeric_token,
                invalid_numeric_token,
            ),
            max_size=50,
        )
    )

    s = "".join(raw for raw, _ in tokens)
    expected = "".join(unescaped for _, unescaped in tokens)

    assert html.unescape(s) == expected
# End program