from hypothesis import given, strategies as st
import html
import re

@given(st.text())
def test_no_character_references(s):
    unescaped = html.unescape(s)
    assert '&' not in unescaped or ';' not in unescaped

@given(st.text())
def test_output_length(s):
    unescaped = html.unescape(s)
    assert len(unescaped) >= len(s)

@given(st.text())
def test_contains_input_characters(s):
    unescaped = html.unescape(s)
    for char in s:
        if char not in ['&', ';']:
            assert char in unescaped

@given(st.text().filter(lambda s: '&' not in s and ';' not in s))
def test_unchanged_input(s):
    unescaped = html.unescape(s)
    assert unescaped == s

@given(st.text())
def test_valid_unicode(s):
    unescaped = html.unescape(s)
    assert bool(re.match(r'^(?:\w|\W)*$', unescaped, re.UNICODE))
# End program