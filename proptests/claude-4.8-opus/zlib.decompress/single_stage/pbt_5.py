from hypothesis import given, strategies as st
import zlib

# Summary: Round-trip test. Generate random payloads, compress them with a chosen
# window-size logarithm and format (zlib / raw / gzip), then decompress with a
# compatible wbits (including auto-detect modes) and a separately chosen bufsize.
# Check that decompress is the inverse of compress, returns bytes, and that the
# result is independent of bufsize.
@given(st.data())
def test_zlib_decompress(data):
    payload = data.draw(st.binary(min_size=0, max_size=4096))
    # Window-size logarithm (must be >= the one used to compress).
    wbits_log = data.draw(st.integers(min_value=9, max_value=15))
    # Choose a format and derive compatible compress/decompress wbits.
    fmt = data.draw(st.sampled_from(["zlib", "raw", "gzip"]))

    if fmt == "zlib":
        compress_wbits = wbits_log  # +8..+15 -> zlib header/trailer
        # Decompress: explicit zlib window, auto-from-header (0), or auto zlib/gzip (32+).
        decompress_wbits = data.draw(st.sampled_from([wbits_log, 0, 32 + wbits_log]))
    elif fmt == "raw":
        compress_wbits = -wbits_log  # -8..-15 -> raw stream, no header/trailer
        # Raw must be decompressed as raw with a window >= the compression window.
        dec_log = data.draw(st.integers(min_value=wbits_log, max_value=15))
        decompress_wbits = -dec_log
    else:  # gzip
        compress_wbits = 16 + wbits_log  # +24..+31 -> gzip header/trailer
        # Decompress: explicit gzip window, or auto zlib/gzip (32+).
        decompress_wbits = data.draw(st.sampled_from([16 + wbits_log, 32 + wbits_log]))

    bufsize = data.draw(st.integers(min_value=1, max_value=8192))

    compressor = zlib.compressobj(wbits=compress_wbits)
    compressed = compressor.compress(payload) + compressor.flush()

    # Property 1 & 2: round-trip recovers original data, result is bytes.
    result = zlib.decompress(compressed, decompress_wbits, bufsize)
    assert isinstance(result, bytes)
    assert result == payload

    # Property 3: bufsize does not affect the decompressed result.
    result_default = zlib.decompress(compressed, decompress_wbits)
    assert result_default == result
# End program