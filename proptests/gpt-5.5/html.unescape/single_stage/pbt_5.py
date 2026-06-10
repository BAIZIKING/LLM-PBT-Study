from hypothesis import given, strategies as st

# Summary: Generate input strings as random concatenations of plain Unicode text
# without '&', valid HTML5 named references, valid decimal/hex numeric references,
# documented examples, invalid numeric references, and unknown named references.
# Property: html.unescape(s) should replace generated valid references with their
# Unicode characters, apply selected HTML5 invalid-reference rules, leave unknown
# references/plain text unchanged, and do this non-recursively over the whole string.
@given(st.data())
def test_html_unescape(data):
    import html
    from html.entities import html5

    named_entities = tuple(name for name in html5 if name.endswith(";"))

    plain_text = st.text(
        alphabet=st.characters(
            blacklist_characters="&",
            blacklist_categories=("Cs",),
        ),
        max_size=30,
    )

    valid_numeric_char = st.characters(
        blacklist_categories=("Cc", "Cn", "Cs"),
    )

    documented_examples = (
        ("&gt;", ">"),
        ("&#62;", ">"),
        ("&#x3e;", ">"),
    )

    invalid_numeric_examples = (
        ("&#0;", "\uFFFD"),
        ("&#xD800;", "\uFFFD"),
        ("&#x110000;", "\uFFFD"),
        ("&#x80;", "\u20AC"),
    )

    parts = []
    expected_parts = []

    for _ in range(data.draw(st.integers(min_value=0, max_value=25))):
        kind = data.draw(
            st.sampled_from(
                (
                    "plain",
                    "named",
                    "decimal_numeric",
                    "hex_numeric",
                    "documented_example",
                    "invalid_numeric",
                    "unknown_named",
                )
            )
        )

        if kind == "plain":
            text = data.draw(plain_text)
            parts.append(text)
            expected_parts.append(text)

        elif kind == "named":
            name = data.draw(st.sampled_from(named_entities))
            parts.append("&" + name)
            expected_parts.append(html5[name])

        elif kind == "decimal_numeric":
            char = data.draw(valid_numeric_char)
            parts.append(f"&#{ord(char)};")
            expected_parts.append(char)

        elif kind == "hex_numeric":
            char = data.draw(valid_numeric_char)
            parts.append(f"&#x{ord(char):X};")
            expected_parts.append(char)

        elif kind == "documented_example":
            token, replacement = data.draw(st.sampled_from(documented_examples))
            parts.append(token)
            expected_parts.append(replacement)

        elif kind == "invalid_numeric":
            token, replacement = data.draw(st.sampled_from(invalid_numeric_examples))
            parts.append(token)
            expected_parts.append(replacement)

        else:
            token = "&__not_an_html5_entity__;"
            parts.append(token)
            expected_parts.append(token)

    s = "".join(parts)
    expected = "".join(expected_parts)

    assert html.unescape(s) == expected

# End program