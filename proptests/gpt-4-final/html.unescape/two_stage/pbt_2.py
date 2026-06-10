from hypothesis import given, strategies as st
import html

#given a string
@given(st.text())
def test_string_length_preservation_property(s):
    #Ensure the output length is less than the input length if there's an escape sequence
    assert len(html.unescape(s)) <= len(s)

@given(st.text())
def test_idempotency_property(s):
    #Make sure that application of the function more than once does not change the result
    assert html.unescape(html.unescape(s)) == html.unescape(s)

@given(st.text())
def test_html_conformance(s):
    #Ensure that the output does not contain any named or numeric character references
    assert '&' not in html.unescape(s) and '<' not in html.unescape(s) and '>' not in html.unescape(s) and '"' not in html.unescape(s)

@given(st.text())
def test_unicode_character_inclusion(s):
    #Check that an escaped sequence gets converted to the right unicode.
    assert html.unescape('&gt;') == '>' 

@given(st.text())
def test_special_character_absence(s):
    #HTML unescape should not produce any reserve special HTML characters
    assert html.unescape('&amp;&lt;&gt;&quot;') == '<>&"'
