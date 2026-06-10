"""
Note: Claude generated 5 separate Python snippets. I merged them into one by removing extraneous imports.
"""
from hypothesis import given, strategies as st
import html
import re

# Strategy: arbitrary text, bounded to avoid pathological huge inputs.
text_strategy = st.text(max_size=1000)

# A regex matching a valid HTML entity that html.escape can produce.
_VALID_ENTITY = re.compile(r'&(amp|lt|gt|quot|#x27);')


@given(s=text_strategy, quote=st.booleans())
def test_no_raw_ampersand(s, quote):
    # Property 1: every '&' in the output begins a recognized escape sequence.
    out = html.escape(s, quote=quote)
    # Find all positions of '&' and ensure each starts a valid entity.
    for m in re.finditer(r'&', out):
        idx = m.start()
        assert _VALID_ENTITY.match(out, idx), \
            f"Raw '&' not starting a valid entity at index {idx} in {out!r}"
# End program


text_strategy = st.text(max_size=1000)


@given(s=text_strategy, quote=st.booleans())
def test_no_raw_angle_brackets():
    pass


@given(s=st.text(max_size=1000), quote=st.booleans())
def test_no_raw_angle_brackets(s, quote):
    # Property 2: output never contains raw '<' or '>', regardless of quote.
    out = html.escape(s, quote=quote)
    assert '<' not in out
    assert '>' not in out
# End program


@given(s=st.text(max_size=1000), quote=st.booleans())
def test_quote_handling(s, quote):
    # Property 3: quote controls escaping of '"' and "'".
    out = html.escape(s, quote=quote)
    if quote:
        assert '"' not in out
        assert "'" not in out
    else:
        # With quote=False, these characters must be preserved unchanged.
        # The number of '"' and "'" in output equals that in input.
        assert out.count('"') == s.count('"')
        assert out.count("'") == s.count("'")
# End program


def _special_chars(quote):
    chars = {'&', '<', '>'}
    if quote:
        chars |= {'"', "'"}
    return chars


# Strategy that generates strings without any special characters.
@given(
    s=st.text(
        alphabet=st.characters(blacklist_characters='&<>"\''),
        max_size=1000,
    ),
    quote=st.booleans(),
)
def test_identity_when_no_special_chars(s, quote):
    # Property 4: if input contains no special chars, output equals input.
    out = html.escape(s, quote=quote)
    assert out == s
# End program


@given(s=st.text(max_size=1000), quote=st.booleans())
def test_output_length_not_shorter(s, quote):
    # Property 5: output length >= input length.
    out = html.escape(s, quote=quote)
    assert len(out) >= len(s)
# End program