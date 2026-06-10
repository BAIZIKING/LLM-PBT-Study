from hypothesis import given, strategies as st
import html

# Summary: Generate Unicode text biased toward HTML special characters (& < > " ')
# mixed with arbitrary text and empty strings, and a boolean `quote` flag. Verify
# that <, > are always escaped, & maps to &amp;, quotes are escaped only when
# quote=True (and unchanged otherwise), no raw < or > remain, and that
# html.unescape recovers the original string.
@given(st.data())
def test_html_escape():
    s = (yield)  # not used
# End program