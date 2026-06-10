from hypothesis import given, strategies as st
import zlib

# Summary: Generate random `data` as arbitrary bytes (covering empty and large inputs),
# `level` as integers in [-1, 9] (all valid compression levels including special values),
# and `wbits` from the three documented valid ranges: +9..+15 (zlib), -9..-15 (raw),
# and +25..+31 (gzip). Check that compress returns bytes and that decompressing with
# the same wbits losslessly recovers the original data.
@given(st.data())
def test_zlib_compress(data):
    payload = data.draw(st.binary(min_size=0, max_size=4096))
    level = data.draw(st.integers(min_value=-1, max_value=9))
    wbits = data.draw(
        st.one_of(
            st.integers(min_value=9, max_value=15),    # zlib header/trailer
            st.integers(min_value=-15, max_value=-9),  # raw stream
            st.integers(min_value=25, max_value=31),   # gzip header/trailer
        )
    )

    compressed = zlib.compress(payload, level, wbits)

    # Property 1: Return type is bytes
    assert isinstance(compressed, bytes)

    # Property 2: Round-trip — decompressing with the same wbits recovers original data
    decompressed = zlib.decompress(compressed, wbits)
    assert decompressed == payload
# End program