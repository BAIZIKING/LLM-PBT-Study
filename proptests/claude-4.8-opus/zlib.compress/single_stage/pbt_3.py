from hypothesis import given, strategies as st
import zlib

# Summary: Generate arbitrary byte data with valid level (-1..9) and wbits
# sampled from the three valid disjoint ranges (+9..+15 zlib, -9..-15 raw,
# +25..+31 gzip). Check return type is bytes and that decompression with a
# matching wbits round-trips back to the original data (lossless compression).
@given(st.data())
def test_zlib_compress(data):
    payload = data.draw(st.binary(min_size=0, max_size=2048))
    level = data.draw(st.integers(min_value=-1, max_value=9))
    wbits = data.draw(
        st.one_of(
            st.integers(min_value=9, max_value=15),    # zlib header
            st.integers(min_value=-15, max_value=-9),  # raw stream
            st.integers(min_value=25, max_value=31),   # gzip header
        )
    )

    compressed = zlib.compress(payload, level=level, wbits=wbits)

    # Property 1: result is always bytes
    assert isinstance(compressed, bytes)

    # Determine matching wbits for decompression based on format used.
    if wbits < 0:
        # raw stream: decompress with the same negative wbits
        decomp_wbits = wbits
    elif wbits >= 25:
        # gzip: decompress with same wbits (16 + window log)
        decomp_wbits = wbits
    else:
        # zlib: decompress with same wbits
        decomp_wbits = wbits

    # Property 2: round-trip is lossless
    restored = zlib.decompress(compressed, wbits=decomp_wbits)
    assert restored == payload
# End program