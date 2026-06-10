from hypothesis import given, strategies as st
import html

NO_AMP_TEXT = st.text(
    alphabet=st.characters(blacklist_characters="&", blacklist_categories=("Cs",)),
    max_size=200,
)

NAMED_REFERENCES = st.sampled_from(
    [
        ("&" + name, value)
        for name, value in html.entities.html5.items()
        if name.endswith(";")
    ]
)

SAFE_NUMERIC_CODEPOINTS = st.integers(min_value=0x20, max_value=0x7E)

DECIMAL_NUMERIC_REFERENCES = SAFE_NUMERIC_CODEPOINTS.map(
    lambda n: ("&#" + str(n) + ";", chr(n))
)

HEXADECIMAL_NUMERIC_REFERENCES = st.tuples(
    SAFE_NUMERIC_CODEPOINTS,
    st.sampled_from(("x", "X")),
).map(
    lambda pair: ("&#" + pair[1] + format(pair[0], "x") + ";", chr(pair[0]))
)

REFERENCE_OR_TEXT_TOKENS = st.one_of(
    NO_AMP_TEXT.map(lambda s: (s, s)),
    NAMED_REFERENCES,
    DECIMAL_NUMERIC_REFERENCES,
    HEXADECIMAL_NUMERIC_REFERENCES,
)


@given(st.data())
def test_html_unescape_output_is_string(data):
    s = data.draw(st.text(max_size=500))
    result = html.unescape(s)
    assert isinstance(result, str)


@given(st.data())
def test_html_unescape_leaves_strings_without_ampersands_unchanged(data):
    s = data.draw(NO_AMP_TEXT)
    result = html.unescape(s)
    assert result == s


@given(st.data())
def test_html_unescape_replaces_valid_named_character_references(data):
    prefix = data.draw(NO_AMP_TEXT)
    reference, expected_character = data.draw(NAMED_REFERENCES)
    suffix = data.draw(NO_AMP_TEXT)

    result = html.unescape(prefix + reference + suffix)

    assert result == prefix + expected_character + suffix


@given(st.data())
def test_html_unescape_replaces_valid_numeric_character_references(data):
    prefix = data.draw(NO_AMP_TEXT)
    reference, expected_character = data.draw(
        st.one_of(DECIMAL_NUMERIC_REFERENCES, HEXADECIMAL_NUMERIC_REFERENCES)
    )
    suffix = data.draw(NO_AMP_TEXT)

    result = html.unescape(prefix + reference + suffix)

    assert result == prefix + expected_character + suffix


@given(st.data())
def test_html_unescape_preserves_non_reference_text_order(data):
    tokens = data.draw(st.lists(REFERENCE_OR_TEXT_TOKENS, max_size=50))

    source = "".join(token_source for token_source, _ in tokens)
    expected = "".join(token_expected for _, token_expected in tokens)

    result = html.unescape(source)

    assert result == expected


# End program