from hypothesis import given, strategies as st
import html

# Define a strategy for generating strings with potential HTML escape sequences
# Limit string length and character range to avoid overflows and very large inputs
string_strategy = st.text(alphabet=st.characters(min_codepoint=0, max_codepoint=127), max_size=1000)

@given(string_strategy)
def test_unescape_output_is_string(s):
    unescaped_string = html.unescape(s)
    assert isinstance(unescaped_string, str)

@given(string_strategy)
def test_unescape_length_leq_input(s):
    unescaped_string = html.unescape(s)
    assert len(unescaped_string) <= len(s)

@given(string_strategy)
def test_unescape_unchanged_chars(s):
    unescaped_string = html.unescape(s)
    for i, char in enumerate(s):
        if char not in "&;":  # Ignore potential escape sequence start characters
            assert unescaped_string[i] == char

@given(st.just("&gt;"), st.just("&#62;"), st.just("&#x3e;"))
def test_unescape_valid_sequences(s):
    assert html.unescape(s) == ">"

@given(st.just("&invalid;"))
def test_unescape_invalid_sequence(s):
    # Replace invalid sequences with � (Unicode replacement character)
    assert html.unescape(s) == "�"
# End program