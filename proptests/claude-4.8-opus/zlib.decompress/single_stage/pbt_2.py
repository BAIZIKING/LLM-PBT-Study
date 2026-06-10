from hypothesis import given, strategies as st
import zlib

# Summary: Generate random byte payloads and compress them with a chosen window
# size and format (zlib / raw / gzip). Then decompress using a compatible wbits
# (including the "auto" modes 0 and 32+) and a varied bufsize. Verify the
# round-trip returns the original bytes, the result is a bytes object, and that
# bufsize does not affect the decompressed output.
@given(st.data())
def test_zlib_decompress(data):
    payload = data.draw(st.binary(min_size=0, max_size=2048))

    # Window-size logarithm used for compression (8..15).
    comp_window = data.draw(st.integers(min_value=9, max_value=15))

    # Choose a format: 'zlib', 'raw', or 'gzip'.
    fmt = data.draw(st.sampled_from(["zlib", "raw", "gzip"]))

    # Decompression window must be >= compression window.
    decomp_window = data.draw(st.integers(min_value=comp_window, max_value=15))

    # Build compress and decompress wbits according to the chosen format,
    # and gather valid decompress wbits options (including auto modes).
    if fmt == "zlib":
        comp_wbits = comp_window
        # +8..+15 (explicit zlib), 0 (auto window), 32+ (auto zlib/gzip).
        decomp_options = [
            decomp_window,
            0,
            32 + decomp_window,
        ]
    elif fmt == "raw":
        comp_wbits = -comp_window
        # raw must use negative wbits; no auto mode for raw.
        decomp_options = [-decomp_window]
    else:  # gzip
        comp_wbits = 16 + comp_window
        # gzip explicit, or 32+ auto zlib/gzip.
        decomp_options = [
            16 + decomp_window,
            32 + decomp_window,
        ]

    decomp_wbits = data.draw(st.sampled_from(decomp_options))

    # Compress the payload with the chosen window/format.
    co = zlib.compressobj(level=data.draw(st.integers(0, 9)), wbits=comp_wbits)
    compressed = co.compress(payload) + co.flush()

    # bufsize edge cases: from very small (forces buffer growth) up to large.
    bufsize = data.draw(st.integers(min_value=1, max_value=4096))

    result = zlib.decompress(compressed, decomp_wbits, bufsize)

    # Property: result is a bytes object.
    assert isinstance(result, bytes)

    # Property: round-trip correctness.
    assert result == payload

    # Property: bufsize does not affect the output (only allocation behavior).
    other_bufsize = data.draw(st.integers(min_value=1, max_value=4096))
    result_other = zlib.decompress(compressed, decomp_wbits, other_bufsize)
    assert result_other == result
# End program