from hypothesis import given, strategies as st
import html

# Summary: Generates random strings with HTML entities and checks for correct unescaping and idempotence.
@given(st.text(alphabet=st.characters(blacklist_categories=("C", "Cs")) | st.html_entities()))
def test_html_unescape(s):
    unescaped_s = html.unescape(s)
    # Check correct unescaping
    assert unescaped_s == html.unescape(unescaped_s)
    # Check idempotence
    assert unescaped_s == html.unescape(html.unescape(s))
    # Check non-entity characters remain unchanged
    for char in unescaped_s:
        if not html.entities.html5.is_valid_entity(char):
            assert char in s

# End program