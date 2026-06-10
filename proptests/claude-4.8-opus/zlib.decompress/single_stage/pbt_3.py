from hypothesis import given, strategies as st
import zlib

# Summary: Generate a random binary payload, then compress it with a randomly
# chosen format family (zlib / raw / gzip / auto-detect) and matching window
# size, producing a (compressed_data, wbits) pair guaranteed valid for
# decompression. Also vary bufsize. Check that decompression round-trips back
# to the original bytes, returns a bytes object, and is independent of bufsize.
@given(st.data())
def test_zlib_decompress(data):
    original = data.draw(st.binary(min_size=0, max_size=2000))
    window = data.draw(st.integers(min_value=9, max_value=15))
    bufsize = data.draw(st.integers(min_value=1, max_value=4096))
    fmt = data.draw(st.sampled_from(["zlib", "raw", "gzip", "auto"]))

    if fmt == "zlib":
        compress_wbits = window           # +8..+15
        decompress_wbits = window
    elif fmt == "raw":
        compress_wbits = -window          # -8..-15
        decompress_wbits = -window
    elif fmt == "gzip":
        compress_wbits = 16 + window      # +24..+31
        decompress_wbits = 16 + window
    else:  # auto: accepts either zlib or gzip
        # randomly compress as zlib or gzip
        use_gzip = data.draw(st.booleans())
        compress_wbits = (16 + window) if use_gzip else window
        decompress_wbits = 32 + window    # +40..+47

    co = zlib.compressobj(level=6, wbits=compress_wbits)
    compressed = co.compress(original) + co.flush()

    # Property 1 & 2: round-trip correctness and bytes return type
    result = zlib.decompress(compressed, wbits=decompress_wbits, bufsize=bufsize)
    assert isinstance(result, bytes)
    assert result == original

    # Property 3: result is independent of the initial bufsize
    result_other = zlib.decompress(compressed, wbits=decompress_wbits, bufsize=1)
    assert result_other == result
# End program