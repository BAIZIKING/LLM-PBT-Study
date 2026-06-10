from hypothesis import given, strategies as st
import zlib

# Summary: Generate random original data and compress it using a randomly chosen
# format (raw / zlib / gzip) with a window-size log in [9,15]. Then decompress
# using a `wbits` that is compatible with how it was compressed: the same value,
# an auto-detect value (0 for zlib, 40+ for zlib/gzip), and whose window is never
# smaller than the compression window. `bufsize` is varied from small to large
# to ensure buffer-growth correctness. We then check that decompression returns
# bytes and round-trips back to the original data.
@given(st.data())
def test_zlib_decompress(data):
    original = data.draw(st.binary(min_size=0, max_size=2000))

    # Choose a compression window-size logarithm in the valid [9, 15] range.
    comp_log = data.draw(st.integers(min_value=9, max_value=15))

    # Choose a format and build compatible (compress_wbits, decompress_wbits).
    fmt = data.draw(st.sampled_from(["raw", "zlib", "gzip"]))

    if fmt == "raw":
        compress_wbits = -comp_log
        # Raw must be decompressed as raw; window log must be >= comp_log.
        decomp_log = data.draw(st.integers(min_value=comp_log, max_value=15))
        decompress_wbits = -decomp_log
    elif fmt == "zlib":
        compress_wbits = comp_log
        # Decompress with same/larger zlib window, auto-detect (0),
        # or auto-accept zlib/gzip (32 + log).
        decomp_log = data.draw(st.integers(min_value=comp_log, max_value=15))
        decompress_wbits = data.draw(st.sampled_from([
            decomp_log,        # explicit zlib window
            0,                 # auto-detect window from zlib header
            32 + decomp_log,   # auto-accept zlib/gzip
        ]))
    else:  # gzip
        compress_wbits = 16 + comp_log
        decomp_log = data.draw(st.integers(min_value=comp_log, max_value=15))
        decompress_wbits = data.draw(st.sampled_from([
            16 + decomp_log,   # explicit gzip window
            32 + decomp_log,   # auto-accept zlib/gzip
        ]))

    # Produce a definitely-valid compressed stream for the chosen format.
    compressor = zlib.compressobj(level=6, wbits=compress_wbits)
    compressed = compressor.compress(original) + compressor.flush()

    # Vary bufsize across small and larger values.
    bufsize = data.draw(st.integers(min_value=1, max_value=4096))

    result = zlib.decompress(compressed, decompress_wbits, bufsize)

    # Property 1: result is a bytes object.
    assert isinstance(result, bytes)

    # Property 2 & 3: round-trip correctness, independent of bufsize.
    assert result == original
# End program