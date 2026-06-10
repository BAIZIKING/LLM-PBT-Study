from hypothesis import given, strategies as st
import html

#given decorator is used to define the strategies for generating input data.

@given(input_string = st.text(), quote_flag = st.booleans())
def test_html_escape_prop(input_string, quote_flag):
    result = html.escape(input_string, quote_flag)
    # property 1
    assert isinstance(result,str)
    # property 2
    if '&' in input_string or '>' in input_string or '<' in input_string:
        assert ('&amp;' in result or '&lt;' in result or '&gt;' in result)
    else:
        assert not('&amp;' in result or '&lt;' in result or '&gt;' in result)
    # property 3
    if quote_flag:
        if '"' in input_string or '\'' in input_string:
            assert ('&quote;' in result or '&apos;' in result)
        else:
            assert not ('&quote;' in result or '&apos;' in result)
    # property 4
    if not('&' in input_string or '>' in input_string or '<' in input_string or '\"' in input_string or '\'' in input_string):
        assert result == input_string
    # property 5
    if input_string == '':
        assert result == ''

test_html_escape_prop()
# End program