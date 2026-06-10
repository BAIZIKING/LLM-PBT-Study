import zlib
from hypothesis import given, strategies as st

# Test that zlib.decompress works correctly with random parameters
@given(st.binary(), st.integers(-15, 47), st.integers())
def test_zlib_decompress(data, wbits, bufsize):
    # The data may not be valid compressed data, in which case an error is expected
    try:
        result = zlib.decompress(data, wbits, bufsize)
        assert isinstance(result, bytes)
        if data:
            assert result != data
        else: 
            assert result == b''
        # Check if the input was valid compressed data by recompressing result and comparing it to data
        if wbits >= 0 and wbits < 16: 
            try:
                reco = zlib.compress(result, wbits+16)
                assert reco == data
            except:
                pass
    except Exception as e:
        # Catching any exceptions are expected as data may not always be valid compressed data
        assert isinstance(e, zlib.error)
# End program