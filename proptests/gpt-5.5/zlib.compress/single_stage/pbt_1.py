from hypothesis import given, strategies as st
import zlib

# Summary: Generate arbitrary byte strings, including empty and large inputs, plus valid compression
# levels (-1, 0..9) and valid wbits values from all documented modes: zlib header/trailer
# (+9..+15), raw deflate (-9..-15), and gzip header/trailer (+25..+31). Check that compression
# returns bytes, is deterministic, and round-trips through zlib.decompress using the same wbits mode.
@given(st.data())
def test_zlib_compress(data):
    input_data = data.draw(st.binary(), label="data")
    level = data.draw(st.integers(min_value=-1, max_value=9), label="level")
    wbits = data.draw(
        st.one_of(
            st.integers(min_value=9, max_value=15),
            st.integers(min_value=-15, max_value=-9),
            st.integers(min_value=25, max_value=31),
        ),
        label="wbits",
    )

    compressed = zlib.compress(input_data, level=level, wbits=wbits)

    assert isinstance(compressed, bytes)
    assert compressed == zlib.compress(input_data, level=level, wbits=wbits)
    assert zlib.decompress(compressed, wbits=wbits) == input_data
# End program