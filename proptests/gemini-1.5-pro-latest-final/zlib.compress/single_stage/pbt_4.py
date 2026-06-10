from hypothesis import given, strategies as st
import zlib

# Summary: Generates random data, compression levels, and window sizes to test zlib.compress behavior
@given(
    data=st.binary(),
    level=st.integers(min_value=-1, max_value=9),
    wbits=st.one_of(
        st.integers(min_value=9, max_value=15),
        st.integers(min_value=-15, max_value=-9),
        st.integers(min_value=25, max_value=31),
    ),
)
def test_zlib_compress(data, level, wbits):
    compressed = zlib.compress(data, level=level, wbits=wbits)

    # Check output type
    assert isinstance(compressed, bytes)

    # Check compression ratio based on level
    if level == 0:
        assert len(compressed) == len(data)
    elif 0 < level <= 9:
        assert len(compressed) <= len(data)

    # Check decompression
    decompressed = zlib.decompress(compressed, wbits=wbits)
    assert decompressed == data

# End program