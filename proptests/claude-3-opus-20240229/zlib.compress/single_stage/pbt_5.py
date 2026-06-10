from hypothesis import given, strategies as st
import zlib

# Summary: Generate a wide variety of byte strings and compression settings to test zlib.compress
# - Generate random printable ASCII text of varying lengths
# - Sometimes generate edge cases like empty string, very long string, non-ASCII bytes 
# - Generate valid compression levels from 0-9 and -1 (default)
# - Generate valid wbits values that cover the allowed ranges
# - Check that compress always returns a bytes object
# - Check that compress with level=0 returns input data unchanged
# - Check that compressed output is different than input (except for level 0)
# - Check that compress with raw wbits does not include header
# - Check that compress with gzip wbits includes gzip headers
@given(
    st.text(alphabet=st.characters(min_codepoint=32, max_codepoint=126), min_size=0, max_size=1000)
    | st.binary(min_size=0, max_size=1000) | st.just(b''),
    st.integers(min_value=0, max_value=9) | st.just(-1),
    st.sampled_from([-15, -9, 9, 15, 31])
)
def test_zlib_compress(data, level, wbits):
    input_data = data.encode('latin-1') if isinstance(data, str) else data
    z = zlib.compress(input_data, level=level, wbits=wbits)
    
    assert isinstance(z, bytes)
    if level == 0:
        assert z == input_data
    else:
        assert z != input_data
    if -15 <= wbits <= -9:  # raw compress
        assert z[0] != 0x78  # no zlib header
    if 25 <= wbits <= 31:  # gzip
        assert z.startswith(b'\x1f\x8b')  # has gzip header
# End program