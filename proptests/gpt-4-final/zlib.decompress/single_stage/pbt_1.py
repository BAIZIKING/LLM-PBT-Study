from hypothesis import given, example, strategies as st
import zlib

@given(
    compressed_data=st.binary(min_size=1), 
    wbits=st.integers(min_value=-15, max_value=47), 
    bufsize=st.integers(min_value=1)
)
def test_zlib_decompress(compressed_data, wbits, bufsize):
    try:
        # Attempt to decompress the generated data
        decompressed = zlib.decompress(compressed_data, wbits, bufsize)
        # Perform further checks here - this is up to your specific requirements
        
    except Exception as e:
        # when 'wbits' is out of indicated intervals, respectively 
        # +8 to +15, 0, -8 to -15, +24 to +31, +40 to +47
        if not (8 <= wbits <= 15 or wbits == 0 or -15 <= wbits <= -8 
                or 24 <= wbits <= 31 or 40 <= wbits <= 47):
            assert isinstance(e, zlib.error)
        else:
            raise
# End program