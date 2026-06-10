
from hypothesis import given, strategies as st
from html import unescape

@given(st.text(min_size=0, max_size=100, alphabet=st.characters(whitelist_categories=("P", "S", "Zs", "C"))).map(lambda s: s.replace('>', '&gt;').replace('<', '&lt;').replace('"', '&quot;').replace("'", '&#39;').replace("©", '&copy;')))
def test_html_unescape(s):
    unescaped = unescape(s)

    # Verify the type - must be a string
    assert type(unescaped) == str

    # Verify that &gt; and &lt; are replaced correctly
    assert '&gt;' not in unescaped and '&lt;' not in unescaped

    # Verify that &quot; and &#39; replaced correctly
    assert '&quot;' not in unescaped and '&#39;' not in unescaped 

    # Verify that &copy; is replaced correctly
    assert '&copy;' not in unescaped
# End program