from hypothesis import given, strategies as st
import zlib

# Summary: Generates random byte sequences, compression levels, and window bits to test zlib.compress behavior.
@given(st.data())
def test_zlib_compress(data):
    input_data = data.draw(st.binary())
    level = data.draw(st.integers(min_value=-1, max_value=9))
    wbits = data.draw(st.one_of(
        st.integers(min_value=9, max_value=15),
        st.integers(min_value=-15, max_value=-9),
        st.integers(min_value=25, max_value=31)
    ))

    compressed_data = zlib.compress(input_data, level=level, wbits=wbits)

    # Property checks
    assert isinstance(compressed_data, bytes)

    # Compare compression ratios for different levels (if applicable)
    if level > 0:
        lower_level_data = zlib.compress(input_data, level=level-1, wbits=wbits)
        assert len(compressed_data) <= len(lower_level_data)

    # Check decompression with appropriate wbits
    decompressed_data = zlib.decompress(compressed_data, wbits=wbits)
    assert decompressed_data == input_data
    
    # Error handling (example for invalid level)
    with pytest.raises(zlib.error):
        zlib.compress(input_data, level="invalid")

# End program