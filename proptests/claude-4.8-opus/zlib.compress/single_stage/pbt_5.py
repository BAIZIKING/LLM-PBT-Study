from hypothesis import given, strategies as st
import zlib

# Summary: Generate random bytes (including empty/large), levels in [-1, 9],
# and wbits sampled from all three valid ranges (zlib +9..+15, raw -9..-15,
# gzip +25..+31). Check return type, determinism, and that decompressing the
# compressed output (with matching wbits) round-trips back to the original data.
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

    # Property 1: return type is bytes
    assert isinstance(compressed, bytes)

    # Property 2: determinism - same inputs produce same output
    compressed_again = zlib.compress(payload, level, wbits)
    assert compressed == compressed_again

    # Property 3: round-trip correctness with matching wbits
    decompressed = zlib.decompress(compressed, wbits)
    assert decompressed == payload
# End program