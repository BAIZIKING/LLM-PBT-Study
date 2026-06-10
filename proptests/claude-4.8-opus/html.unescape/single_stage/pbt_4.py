from hypothesis import given, strategies as st
import html
from html.entities import html5

# Summary: Generate composite strings mixing arbitrary text, official HTML5
# named references, and decimal/hex numeric references (including edge
# codepoints). Verify unescape is total (always returns str, never raises),
# correctly expands known named references, and is the inverse of html.escape
# on plain text.
@given(st.data())
def test_html_unescape(data):
    # Strategy components
    plain_text = st.text()
    named_ref = st.sampled_from(list(html5.keys())).map(lambda k: "&" + k)
    dec_ref = st.integers(min_value=0, max_value=0x11FFFF).map(lambda n: f"&#{n};")
    hex_ref = st.integers(min_value=0, max_value=0x11FFFF).map(lambda n: f"&#x{n:x};")

    fragment = st.one_of(plain_text, named_ref, dec_ref, hex_ref)
    composite = data.draw(st.lists(fragment, max_size=20)).__iter__()
    s = "".join(composite)

    # Property 1: totality — always returns a str, never raises.
    result = html.unescape(s)
    assert isinstance(result, str)

    # Property 2: known named references expand correctly.
    name = data.draw(st.sampled_from(list(html5.keys())))
    expected = html5[name]
    assert html.unescape("&" + name) == expected

    # Property 3: escape then unescape is identity on arbitrary text.
    text = data.draw(st.text())
    assert html.unescape(html.escape(text, quote=True)) == text
# End program