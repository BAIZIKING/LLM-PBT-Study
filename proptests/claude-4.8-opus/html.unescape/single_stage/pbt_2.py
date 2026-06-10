from hypothesis import given, strategies as st
import html
from html.entities import html5

# Summary: Build strings from a mix of plain text, real named refs (from
# html.entities.html5), decimal/hex numeric refs, and malformed refs, then
# join random selections. Check: (a) unescape never crashes and returns str,
# (b) ampersand-free text is returned unchanged, (c) well-formed named refs
# map to their documented Unicode value.
@given(st.data())
def test_html_unescape(data):
    # Real named references (those ending in ';') and their target values.
    named_refs = {k: v for k, v in html5.items() if k.endswith(";")}
    named_keys = sorted(named_refs.keys())

    # Strategy for various kinds of fragments.
    plain_text = st.text(
        alphabet=st.characters(blacklist_characters="&"), max_size=10
    )
    named_ref = st.sampled_from(["&" + k for k in named_keys])
    dec_ref = st.integers(min_value=0, max_value=0x10FFFF).map(lambda n: f"&#{n};")
    hex_ref = st.integers(min_value=0, max_value=0x10FFFF).map(
        lambda n: f"&#x{n:x};"
    )
    malformed = st.sampled_from(
        ["&", "&;", "&#;", "&#x;", "&amp", "&#999999999;", "&notareal;", "&#xZZ;"]
    )

    fragment = st.one_of(plain_text, named_ref, dec_ref, hex_ref, malformed)
    s = data.draw(st.lists(fragment, max_size=8).map("".join))

    # Property (a): total function, always returns a str, never raises.
    result = html.unescape(s)
    assert isinstance(result, str)

    # Property (b): a string with no '&' must be returned unchanged.
    if "&" not in s:
        assert result == s

    # Property (c): a well-formed named reference alone maps to its
    # documented Unicode value.
    key = data.draw(st.sampled_from(named_keys))
    assert html.unescape("&" + key) == named_refs[key]
# End program