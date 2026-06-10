from hypothesis import given, strategies as st, assume
import html

@given(st.text(min_size=1))
def test_html_unescape(input_string):
    try:
        unescaped_string = html.unescape(input_string)
    except:
        assume(False)
    assert '&' not in unescaped_string or ('&' in unescaped_string and ';' in unescaped_string)