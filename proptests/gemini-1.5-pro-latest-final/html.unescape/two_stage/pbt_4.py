from hypothesis import given, strategies as st
import html

# Define a strategy for generating strings with potential HTML entities
string_strategy = st.text(alphabet=st.characters(blacklist_categories=('Cc', 'Cs')), 
                          min_size=1, max_size=100)

@given(string_strategy)
def test_unescape_output_is_string(s):
    unescaped_string = html.unescape(s)
    assert isinstance(unescaped_string, str)

@given(string_strategy)
def test_unescape_length(s):
    unescaped_string = html.unescape(s)
    assert len(unescaped_string) <= len(s)

@given(string_strategy)
def test_unescape_unchanged_chars(s):
    unescaped_string = html.unescape(s)
    for i, char in enumerate(s):
        if char not in html.entities.entitydefs:
            assert unescaped_string[i] == char

@given(st.sampled_from(list(html.entities.entitydefs.keys())))
def test_unescape_valid_entities(entity):
    unescaped_string = html.unescape(f"&{entity};")
    assert unescaped_string == html.entities.entitydefs[entity]

@given(st.text(alphabet=st.characters(blacklist_categories=('Cc', 'Cs'))))
def test_unescape_invalid_entities(entity):
    unescaped_string = html.unescape(f"&{entity};")
    assert unescaped_string == f"&\uFFFD;"  # Check for replacement character
# End program