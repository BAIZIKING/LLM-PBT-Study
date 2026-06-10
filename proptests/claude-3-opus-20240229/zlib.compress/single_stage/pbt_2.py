from hypothesis import given, strategies as st
import zlib

# Summary: Generate a wide variety of byte strings for data, and test compression
# levels from 0 to 9 and -1. For wbits, test values between -15 and -9, between 
# 9 and 15, and between 25 and 31. Verify that compress always returns a bytes
# result that has length > 0 and <= the input data length. Also check that 
# decompressing the result returns the original data.
@given(
    data=st.binary(min_size=0, max_size=1024),
    level=st.integers(min_value=-1, max_value=9),
    wbits=st.one_of(
        st.integers(min_value=-15, max_value=-9), 
        st.integers(min_value=9, max_value=15),
        st.integers(min_value=25, max_value=31)
    )
)
def test_zlib_compress(data, level, wbits):
    result = zlib.compress(data, level=level, wbits=wbits)
    assert isinstance(result, bytes)
    assert 0 < len(result) <= len(data)
    
    decomp = zlib.decompress(result, wbits=wbits)
    assert data == decomp
# End program