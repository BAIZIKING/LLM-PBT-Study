from hypothesis import given, strategies as st
import html
import html.entities

_HTML5_ENTITY_NAMES = [name for name in html.entities.html5 if name.endswith(";")]


def _is_safe_numeric_codepoint(cp):
    return (
        (0x20 <= cp <= 0x10FFFF)
        and not (0x7F <= cp <= 0x9F)
        and not (0xD800 <= cp <= 0xDFFF)
        and not (0xFDD0 <= cp <= 0xFDEF)
        and (cp & 0xFFFF) not in (0xFFFE, 0xFFFF)
    )


_SAFE_CODEPOINTS = st.integers(min_value=0x20, max_value=0x10FFFF).filter(
    _is_safe_numeric_codepoint
)

# Summary: Generate a mix of ampersand-free plain strings, valid HTML5 named references,
# decimal numeric references, hexadecimal numeric references, documented examples, and
# fully arbitrary strings. Check that plain strings are unchanged, generated references
# decode to their documented Unicode character, documented examples decode correctly, and
# arbitrary string inputs always return a string without raising.
@given(st.data())
def test_html_unescape(data):
    no_amp_text = st.text(alphabet=st.characters(blacklist_characters="&"))

    case = data.draw(
        st.sampled_from(
            ["plain", "named", "decimal", "hexadecimal", "documented", "arbitrary"]
        )
    )

    if case == "plain":
        s = data.draw(no_amp_text)
        assert html.unescape(s) == s

    elif case == "named":
        prefix = data.draw(no_amp_text)
        suffix = data.draw(no_amp_text)
        entity_name = data.draw(st.sampled_from(_HTML5_ENTITY_NAMES))

        s = prefix + "&" + entity_name + suffix
        expected = prefix + html.entities.html5[entity_name] + suffix

        assert html.unescape(s) == expected

    elif case == "decimal":
        prefix = data.draw(no_amp_text)
        suffix = data.draw(no_amp_text)
        cp = data.draw(_SAFE_CODEPOINTS)

        s = prefix + f"&#{cp};" + suffix
        expected = prefix + chr(cp) + suffix

        assert html.unescape(s) == expected

    elif case == "hexadecimal":
        prefix = data.draw(no_amp_text)
        suffix = data.draw(no_amp_text)
        cp = data.draw(_SAFE_CODEPOINTS)
        x = data.draw(st.sampled_from(["x", "X"]))
        hex_digits = data.draw(st.sampled_from([format(cp, "x"), format(cp, "X")]))

        s = prefix + f"&#{x}{hex_digits};" + suffix
        expected = prefix + chr(cp) + suffix

        assert html.unescape(s) == expected

    elif case == "documented":
        prefix = data.draw(no_amp_text)
        suffix = data.draw(no_amp_text)
        reference, character = data.draw(
            st.sampled_from([("&gt;", ">"), ("&#62;", ">"), ("&#x3e;", ">")])
        )

        s = prefix + reference + suffix
        expected = prefix + character + suffix

        assert html.unescape(s) == expected

    else:
        s = data.draw(st.text())
        result = html.unescape(s)

        assert isinstance(result, str)

# End program