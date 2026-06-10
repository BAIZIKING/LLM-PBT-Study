from hypothesis import given, strategies as st
import zlib

@given(st.data())
def test_zlib_compress(data):
    bytes_data = data.draw(st.binary())
    level = data.draw(st.integers(min_value=-1, max_value=9))
    wbits_category = data.draw(st.sampled_from([range(9, 16), range(-9, -16, -1), range(25, 32)]))
    wbits = data.draw(st.integers(min_value=min(wbits_category), max_value=max(wbits_category)))

    try:
        result = zlib.compress(bytes_data, level, wbits)
    except Exception as e:
        raise AssertionError("An exception was raised") from e

    # Check the output is a bytes object
    assert isinstance(result, bytes), "Result is not bytes"

    # Check the output is consistent
    assert result == zlib.compress(bytes_data, level, wbits), "Compression results are not consistent"

    # Check the compressed data matches the original when decompressed
    if -9 <= wbits <= -15:
        assert bytes_data == zlib.decompress(result, -wbits), "Compressed data doesn't match original"
    elif 25 <= wbits <= 31:
        assert bytes_data == zlib.decompress(result, wbits - 16), "Compressed data doesn't match original"
    else:
        assert bytes_data == zlib.decompress(result, wbits), "Compressed data doesn't match original"

# End program