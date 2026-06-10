from hypothesis import given, strategies as st
import zlib

# Summary: Generate random bytes for `data`, integers in [-1, 9] for `level`,
# and `wbits` sampled from all three valid ranges (zlib: 9..15, raw: -15..-9,
# gzip: 25..31). Verify the output is bytes, round-trips correctly via
# zlib.decompress with the matching wbits, and carries the correct format header.
@given(st.data())
def test_zlib_compress(data):
    payload = data.draw(st.binary(max_size=2048))
    level = data.draw(st.integers(min_value=-1, max_value=9))
    wbits = data.draw(st.sampled_from(
        list(range(9, 16)) +      # zlib header/trailer
        list(range(-15, -8)) +    # raw, no header/trailer
        list(range(25, 32))       # gzip header/trailer
    ))

    compressed = zlib.compress(payload, level, wbits)

    # Property 1: result is always a bytes object
    assert isinstance(compressed, bytes)

    # Property 2: round-trip correctness with the matching wbits
    decompressed = zlib.decompress(compressed, wbits)
    assert decompressed == payload

    # Property 3: format-specific header checks
    if 25 <= wbits <= 31:
        # gzip output begins with the gzip magic bytes
        assert compressed[:2] == b"\x1f\x8b"
    elif 9 <= wbits <= 15:
        # zlib output includes a header/trailer, so it is non-empty
        assert len(compressed) > 0
# End program