from hypothesis import given, strategies as st
import html

# Summary: Build messy HTML-like strings by mixing named references, decimal/hex
# numeric references, and arbitrary Unicode text. Check that html.unescape never
# raises and returns str, resolves single valid references correctly, is a fixed
# point on strings lacking '&', and round-trips with html.escape.
@given(st.data())
def test_html_unescape(data):
    named = ["&gt;", "&lt;", "&amp;", "&quot;", "&copy;", "&euro;", "&nbsp;"]
    decimal = ["&#62;", "&#65;", "&#38;", "&#960;", "&#0;"]
    hexa = ["&#x3e;", "&#X41;", "&#x26;", "&#x3C0;"]
    arbitrary = st.text()

    # Build a mixed input from random fragments of each category.
    fragment = st.one_of(
        st.sampled_from(named),
        st.sampled_from(decimal),
        st.sampled_from(hexa),
        arbitrary,
    )
    pieces = data.draw(st.lists(fragment, max_size=10))
    s = "".join(pieces)

    # Property 1: total function returning str, never raising.
    result = html.unescape(s)
    assert isinstance(result, str)

    # Property 2: single valid references resolve to their known characters.
    known = {
        "&gt;": ">", "&lt;": "<", "&amp;": "&", "&quot;": '"',
        "&copy;": "\u00a9", "&euro;": "\u20ac", "&nbsp;": "\u00a0",
        "&#62;": ">", "&#65;": "A", "&#38;": "&", "&#960;": "\u03c0",
        "&#x3e;": ">", "&#X41;": "A", "&#x26;": "&", "&#x3C0;": "\u03c0",
    }
    ref = data.draw(st.sampled_from(sorted(known)))
    assert html.unescape(ref) == known[ref]

    # Property 3: strings without '&' are fixed points.
    plain = data.draw(st.text()).replace("&", "")
    assert html.unescape(plain) == plain

    # Property 4: round-trip with html.escape recovers the original text.
    text = data.draw(st.text())
    assert html.unescape(html.escape(text, quote=True)) == text
# End program