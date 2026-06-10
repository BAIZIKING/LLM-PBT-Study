from hypothesis import given, strategies as st
import html

@given(st.text())
def test_output_is_string(s):
    assert isinstance(html.unescape(s), str)

@given(st.text())
def test_unchanged_characters_remain_unchanged(s):
    unescaped_string = html.unescape(s)
    for i, char in enumerate(s):
        if char not in html.entities.entitydefs:
            assert unescaped_string[i] == char

@given(st.integers(min_value=0, max_value=1114111), st.booleans())
def test_numeric_character_references_are_decoded(codepoint, is_hex):
    if is_hex:
        entity = "&#x{:X};".format(codepoint)
    else:
        entity = "&#{};".format(codepoint)
    unescaped_string = html.unescape(entity)
    assert unescaped_string == chr(codepoint)

@given(st.sampled_from(list(html.entities.entitydefs)))
def test_named_character_references_are_decoded(entity):
    unescaped_string = html.unescape("&{};".format(entity))
    assert unescaped_string == html.entities.entitydefs[entity]

@given(st.lists(st.sampled_from(list(html.entities.entitydefs))))
def test_multiple_occurrences_are_decoded(entities):
    text_with_entities = "".join("&{};".format(e) for e in entities)
    unescaped_string = html.unescape(text_with_entities)
    for entity in entities:
        assert html.entities.entitydefs[entity] in unescaped_string
# End program