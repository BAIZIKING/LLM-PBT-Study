from hypothesis import given, strategies as st
import html
import html.entities

# Summary: Generate inputs by mixing arbitrary unicode text, real HTML5 named
# references, decimal/hex numeric references, and malformed entity-like fragments,
# then concatenating them. We verify: (1) unescape always returns a str without
# crashing; (2) escaping arbitrary text and unescaping it round-trips to the
# original (documented inverse behavior for valid references); (3) explicitly
# constructed valid named/numeric references resolve to the documented character.
@given(st.data())
def test_html_unescape(data):
    # --- Strategy components ---
    named_keys = list(html.entities.html5.keys())  # e.g. 'gt;', 'amp;', 'lt;'
    named_ref = data.draw(st.sampled_from(named_keys).map(lambda k: "&" + k))

    codepoint = data.draw(st.integers(min_value=1, max_value=0x10FFFF))
    decimal_ref = "&#" + str(codepoint) + ";"
    hex_ref = "&#x" + format(codepoint, "x") + ";"

    malformed = data.draw(st.sampled_from([
        "&notarealentity;", "&#;", "&#xZZ;", "&amp", "&", "&#999999999999;",
        "&;", "&#x;", "&lt", "&&amp;;",
    ]))

    plain = data.draw(st.text())

    # Compose a mixed input from the pieces above.
    pieces = data.draw(st.lists(
        st.sampled_from([named_ref, decimal_ref, hex_ref, malformed, plain]),
        min_size=0, max_size=6,
    ))
    composed = "".join(pieces)

    # --- Property 1: total function, always returns a str, never crashes ---
    result = html.unescape(composed)
    assert isinstance(result, str)

    # --- Property 2: escape -> unescape round-trips arbitrary text ---
    # html.escape converts &, <, > (and optionally quotes) to valid references;
    # html.unescape must invert this exactly.
    arbitrary = data.draw(st.text())
    assert html.unescape(html.escape(arbitrary, quote=True)) == arbitrary
    assert html.unescape(html.escape(arbitrary, quote=False)) == arbitrary

    # --- Property 3: known valid references resolve correctly ---
    assert html.unescape("&amp;") == "&"
    assert html.unescape("&lt;") == "<"
    assert html.unescape("&gt;") == ">"
    assert html.unescape("&#62;") == ">"
    assert html.unescape("&#x3e;") == ">"
    assert html.unescape("&#x3E;") == ">"

    # A directly-built valid named reference must map to its documented value.
    assert html.unescape(named_ref) == html.entities.html5[named_ref[1:]]
# End program