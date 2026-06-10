from hypothesis import given, strategies as st
import zlib

# Summary: Generates diverse input data, wbits, and bufsize values for zlib.decompress, including edge cases.
@given(data=st.data())
def test_zlib_decompress(data):
    # Generate input data
    input_bytes = data.draw(st.binary())
    
    # Generate wbits
    wbits_strategy = st.sampled_from(list(range(8, 16)) + [0] + list(range(-8, -16, -1)) + list(range(24, 32)) + list(range(40, 48)))
    wbits = data.draw(wbits_strategy)

    # Generate bufsize
    bufsize = data.draw(st.integers(min_value=0))

    # Test decompression
    try:
        decompressed_data = zlib.decompress(input_bytes, wbits=wbits, bufsize=bufsize)
        # Verify output type
        assert isinstance(decompressed_data, bytes)
    except zlib.error:
        # Check if error is expected due to invalid input
        if not isinstance(input_bytes, bytes) or wbits not in range(-15, 16) and wbits not in range(24, 32) and wbits not in range(40, 48):
            pass  # Expected error
        else:
            raise

# End program