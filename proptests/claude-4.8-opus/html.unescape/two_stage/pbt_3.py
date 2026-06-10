from hypothesis import given, strategies as st
import html


# Property 1: Output is always a string.
@given(st.text())
def test_html_unescape_returns_string(s):
    result = html.unescape(s)
    assert isinstance(result, str)


# Property 2: Idempotence for strings with no ampersands.
# A string with no '&' has no character references, so unescaping is idempotent.
@given(st.text().filter(lambda x: "&" not in x))
def test_html_unescape_idempotent_no_ampersand(s):
    once = html.unescape(s)
    twice = html.unescape(once)
    assert once == twice


# Property 3: Known reference mappings produce expected Unicode characters.
@given(st.sampled_from([
    ("&gt;", ">"),
    ("&#62;", ">"),
    ("&#x3e;", ">"),
    ("&#X3E;", ">"),
    ("&amp;", "&"),
    ("&lt;", "<"),
    ("&#60;", "<"),
    ("&#x3c;", "<"),
    ("&quot;", '"'),
    ("&apos;", "'"),
    ("&#38;", "&"),
    ("&copy;", "\u00a9"),
]))
def test_html_unescape_known_mappings(pair):
    reference, expected = pair
    assert html.unescape(reference) == expected


# Property 4: Output length is no greater than input length.
@given(st.text(max_size=1000))
def test_html_unescape_length_not_greater(s):
    result = html.unescape(s)
    assert len(result) <= len(s)


# Property 5: Text without ampersands is returned unchanged.
@given(st.text().filter(lambda x: "&" not in x))
def test_html_unescape_no_ampersand_invariant(s):
    assert html.unescape(s) == s
# End program