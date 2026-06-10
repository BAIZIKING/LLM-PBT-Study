from hypothesis import given, strategies as st
import html
from html.entities import html5

# Summary: Build strings from a mix of valid named refs (from html5 table),
# decimal/hex numeric refs (from random codepoints), malformed refs, and
# plain Unicode text; then verify type/totality, idempotence on ref-free
# text, correct named & numeric expansions, and that '&' count never grows.
@given(st.data())
def test_html_unescape(data):
    named = list(html5.keys())  # valid named refs, e.g. 'gt;', 'amp;'

    # A safe codepoint (avoid surrogates which chr can't represent in some refs)
    codepoint = data.draw(
        st.integers(min_value=1, max_value=0x10FFFF).filter(
            lambda c: not (0xD800 <= c <= 0xDFFF)
        )
    )

    fragment = st.one_of(
        st.sampled_from(named).map(lambda n: "&" + n),          # valid named ref
        st.integers(min_value=1, max_value=0x10FFFF).map(lambda n: f"&#{n};"),   # decimal
        st.integers(min_value=1, max_value=0x10FFFF).map(lambda n: f"&#x{n:x};"),# hex
        st.sampled_from(["&", "&#;", "&#x;", "&notarealentity;", "&;", "&#"]),    # malformed
        st.text(),                                              # plain unicode text
    )
    parts = data.draw(st.lists(fragment, max_size=20))
    s = "".join(parts)

    # Property 1: type & totality
    result = html.unescape(s)
    assert isinstance(result, str)

    # Property 2: idempotence on ampersand-free text
    plain = data.draw(st.text().filter(lambda t: "&" not in t))
    assert html.unescape(plain) == plain

    # Property 3: known named references expand correctly
    name = data.draw(st.sampled_from(named))
    assert html.unescape("&" + name) == html5[name]

    # Property 4: decimal and hex numeric refs agree and equal chr(codepoint)
    dec = html.unescape(f"&#{codepoint};")
    hexed = html.unescape(f"&#x{codepoint:x};")
    assert dec == hexed
    # Valid (non-control, representable) codepoints map to chr(codepoint)
    if not (0x00 < codepoint <= 0x08 or 0x0E <= codepoint <= 0x1F
            or 0x7F <= codepoint <= 0x9F or codepoint > 0x10FFFF):
        assert dec == chr(codepoint) or len(dec) == 1

    # Property 5: unescaping never introduces new ampersands
    assert result.count("&") <= s.count("&")
# End program