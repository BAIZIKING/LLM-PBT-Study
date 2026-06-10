from hypothesis import given, strategies as st
import zlib

# Summary: Generate random payloads, compress them with a randomly chosen valid
# format/window (zlib, raw, or gzip), then decompress with a *compatible* wbits
# (exact match or an auto-detect value) and random bufsize. Properties checked:
# round-trip identity, bytes return type, and bufsize-independence of the output.
@given(st.data())
def test_zlib_decompress(data):
    payload = data.draw(st.binary(min_size=0, max_size=2048))

    # Window-size logarithm (8..15). Use >=9 to safely allow auto-detect/larger windows.
    wlog = data.draw(st.integers(min_value=9, max_value=15))

    # Pick a format to compress with, and a compatible set of decompress wbits.
    fmt = data.draw(st.sampled_from(["zlib", "raw", "gzip"]))

    if fmt == "zlib":
        compress_wbits = wlog                       # +9..+15: zlib header/trailer
        decompress_wbits = data.draw(st.sampled_from([
            wlog,        # exact zlib wbits
            0,           # auto-detect window from zlib header
            32 + wlog,   # auto-accept zlib or gzip
        ]))
    elif fmt == "raw":
        compress_wbits = -wlog                       # -9..-15: raw stream, no header
        decompress_wbits = -wlog                      # must match raw format
    else:  # gzip
        compress_wbits = 16 + wlog                    # +25..+31: gzip header/trailer
        decompress_wbits = data.draw(st.sampled_from([
            16 + wlog,   # exact gzip wbits
            32 + wlog,   # auto-accept zlib or gzip
        ]))

    # Build a valid compressed stream using the matching wbits.
    compressor = zlib.compressobj(level=6, wbits=compress_wbits)
    compressed = compressor.compress(payload) + compressor.flush()

    # Two different bufsizes to verify buffer-growth independence.
    bufsize_a = data.draw(st.integers(min_value=1, max_value=8))
    bufsize_b = data.draw(st.integers(min_value=1024, max_value=65536))

    result_a = zlib.decompress(compressed, wbits=decompress_wbits, bufsize=bufsize_a)
    result_b = zlib.decompress(compressed, wbits=decompress_wbits, bufsize=bufsize_b)

    # Property 2: return type is always bytes.
    assert isinstance(result_a, bytes)
    assert isinstance(result_b, bytes)

    # Property 1: round-trip identity.
    assert result_a == payload

    # Property 3: bufsize is only a performance hint; output is identical.
    assert result_a == result_b
# End program