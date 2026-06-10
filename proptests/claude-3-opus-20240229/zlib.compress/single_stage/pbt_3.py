from hypothesis import given, strategies as st
import zlib

# Summary: Generate a wide range of byte strings for data and all valid
# integer values for level and wbits. Test that the compressed output is 
# shorter than the input, decompresses back to the original data, and
# raises an error if any argument is invalid.
@given(
    data=st.binary(min_size=0, max_size=1000000), 
    level=st.integers(min_value=-1, max_value=9),
    wbits=st.one_of(
        st.integers(min_value=-15, max_value=-9), 
        st.integers(min_value=9, max_value=15),
        st.integers(min_value=25, max_value=31)
    )
)
def test_zlib_compress(data, level, wbits):
    compressed = zlib.compress(data, level=level, wbits=wbits)
    assert len(compressed) <= len(data)
    
    wbits_decompress = wbits
    if wbits < 0:
        wbits_decompress = -wbits_decompress
    else:
        wbits_decompress += 32
    
    decompressed = zlib.decompress(compressed, wbits=wbits_decompress)
    assert data == decompressed

# End program