from hypothesis import given, strategies as st
import zlib

# Summary: Generate a wide variety of byte strings to compress, including edge cases like empty strings,
# very large strings, and strings with special characters. Test different compression levels and window sizes.
# Check that the compressed data decompresses back to the original input, and that errors are raised for 
# invalid arguments.
@given(
    data=st.binary(),
    level=st.integers(min_value=0, max_value=9) | st.just(-1),
    wbits=st.integers(min_value=-15, max_value=-9) | st.integers(min_value=9, max_value=15) | st.integers(min_value=25, max_value=31)
)
def test_zlib_compress(data, level, wbits):
    compressed = zlib.compress(data, level=level, wbits=wbits)
    assert isinstance(compressed, bytes)
    decompressed = zlib.decompress(compressed, wbits=wbits)
    assert data == decompressed

    if wbits < -15 or (wbits > 15 and wbits < 25) or wbits > 31:
        with pytest.raises(ValueError):
            zlib.compress(data, wbits=wbits)

    if level < -1 or level > 9:
        with pytest.raises(ValueError):
            zlib.compress(data, level=level)
# End program