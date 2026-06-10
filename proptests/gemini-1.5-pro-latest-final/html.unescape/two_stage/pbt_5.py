from hypothesis import given, strategies as st
import html

@given(st.text())
def test_no_html_entities_in_output(s):
    unescaped_string = html.unescape(s)
    assert "&" not in unescaped_string and ";" not in unescaped_string

@given(st.text())
def test_output_length_less_than_equal_to_input(s):
    unescaped_string = html.unescape(s)
    assert len(unescaped_string) <= len(s)

@given(st.text())
def test_unchanged_characters_remain_unchanged(s):
    original_chars = [char for char in s if char not in "&;"]
    unescaped_string = html.unescape(s)
    for char in original_chars:
        assert char in unescaped_string

@given(st.text(alphabet=st.characters(blacklist_characters=["&", ";"])))
def test_valid_html_entities_decoded(s):
    # Create a string with valid HTML entities
    entity_string = "&amp;&lt;&gt;&quot;&apos;"
    s_with_entities = s + entity_string
    unescaped_string = html.unescape(s_with_entities)
    assert "&" not in unescaped_string and ";" not in unescaped_string
    assert "<" in unescaped_string and ">" in unescaped_string
    assert '"' in unescaped_string and "'" in unescaped_string

@given(st.text())
def test_invalid_html_entities_handled(s):
    # Insert an invalid HTML entity
    s_with_invalid_entity = s + "&invalid;"
    unescaped_string = html.unescape(s_with_invalid_entity)
    # Assert the invalid entity is either removed or replaced 
    assert unescaped_string in [s, s + "&"]
# End program