from hypothesis import given, strategies as st
from html import unescape

valid_named_references = ['&quot;', '&amp;', '&lt;', '&gt;']
unescaped_valid_named_references = ['"', '&', '<', '>']

@given(st.data())
def test_html_unescape(data):
    escaped_str = data.draw(st.one_of(
                            st.text(min_size=1),  # invalid references
                            st.sampled_from(valid_named_references),  # valid named references
                            st.text('&#{0};', st.integers(min_value=0, max_value=1_114_111))  # valid numeric references
                        ))

    unescaped_str = unescape(escaped_str)

    # Unescaped string must not contain any valid reference
    for valid_ref in valid_named_references:
        assert valid_ref not in unescaped_str

    # Comparing lengths
    assert len(escaped_str) >= len(unescaped_str)