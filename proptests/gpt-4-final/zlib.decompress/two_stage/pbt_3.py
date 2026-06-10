from hypothesis import given, strategies as st
import zlib

@given(st.binary(), st.integers(min_value=-15, max_value=47), st.integers())
def test_zlib_decompress_property(input_data, wbits, bufsize):
    if not (8 <= wbits <= 15 or -15 <= wbits <= -8 or 24 <= wbits <= 31 or 40 <= wbits <= 47 or wbits == 0):
        try:
            zlib.decompress(input_data, wbits, bufsize)
            assert False, "Expected ValueError when wbits is out of valid ranges"
        except ValueError:
            pass
    else:
        try:
            output_data = zlib.decompress(input_data, wbits, bufsize)
            assert isinstance(output_data, bytes), "Output of zlib.decompress is not a bytes object"

            recompression_data = zlib.compress(output_data)
            re_decompression_data = zlib.decompress(recompression_data)
            assert output_data == re_decompression_data, "Output after re-compression and decompression are not same"
        except (ValueError, zlib.error):
            pass