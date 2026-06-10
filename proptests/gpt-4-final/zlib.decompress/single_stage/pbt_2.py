from hypothesis import given, strategies as st
import zlib

@given(st.binary(), st.integers(min_value=-15, max_value=47))
def test_zlib_decompress(data, wbits):
    if wbits >= -15 and wbits <= 47:
        try:
            decompressed_data = zlib.decompress(data, wbits)
            # The return type of zlib.decompress is bytes
            assert isinstance(decompressed_data, bytes)
            # The recompressed data must match with original
            compressed_data_again  = zlib.compress(decompressed_data, wbits)
            assert compressed_data_again == data
        except:
            # If zlib.decompress raise an exception, the data format does not match with the one detected by wbits
            assert True
    else:
        # If wbits is outside the valid range an exception should be raised
        try:
            zlib.decompress(data, wbits)
            assert False, "Expected an Exception!"
        except:
            assert True