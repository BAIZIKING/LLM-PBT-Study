from hypothesis import given, strategies as st
import zlib

# Summary: Generate random bytes for `data` (including empty), all valid
# compression `levels` (-1 through 9), and `wbits` sampled from the three
# documented valid ranges (+9..+15 zlib, -9..-15 raw, +25..+31 gzip).
# Verify the result is bytes and round-trips back to the original data
# when decompressed with the same wbits.
@given(st.data())
def test_zlib_compress(data):
    payload = data.draw(st.binary(min_size=0, max_size=2048))
    level = data.draw(st.integers(min_value=-1, max_value=9))
    wbits = data.draw(
        st.one_of(
            st.integers(min_value=9, max_value=15),    # zlib header/trailer
            st.integers(min_value=-15, max_value=-9),  # raw stream
            st.integers(min_value=25, max_value=31),   # gzip header/trailer
        )
    )

    compressed = zlib.compress(payload, level, wbits)

    # Property 1: result is always bytes
    assert isinstance(compressed, bytes)

    # Property 2: round-trip recovers original data exactly
    # (decompress must use the same wbits to interpret the header format)
    decompressed = zlib.decompress(compressed, wbits)
    assert decompressed == payload
# End program