from hypothesis import given, strategies as st
import zlib

# Summary: Generate either known-valid compressed streams or arbitrary byte strings. Valid streams are built from random payloads using zlib, raw deflate, and gzip formats, random compression levels, window sizes 9..15, compatible documented decompression wbits values, and edge-case bufsize values such as 0, 1, small sizes, the default-sized buffer, and larger buffers. Arbitrary byte strings are paired with documented wbits ranges to exercise malformed/truncated inputs. Properties checked: valid streams round-trip to the original bytes and return bytes; bufsize only affects allocation and therefore must not affect output; arbitrary inputs either raise zlib.error or, if accepted, produce the same bytes for different bufsize values.
_BUF_SIZES = st.one_of(
    st.integers(min_value=0, max_value=64),
    st.sampled_from([0, 1, 2, 7, 8, 15, 16, 255, 256, 1024, 16384, 65536]),
)

_DOCUMENTED_WBITS = (
    list(range(8, 16))
    + [0]
    + list(range(-15, -7))
    + list(range(24, 32))
    + list(range(40, 48))
)


def _compress(payload, level, wbits):
    compressor = zlib.compressobj(level, zlib.DEFLATED, wbits)
    return compressor.compress(payload) + compressor.flush()


def _supports_wbits_zero():
    try:
        zlib.decompress(zlib.compress(b"x"), wbits=0)
    except zlib.error:
        return False
    return True


@given(st.data())
def test_zlib_decompress(data):
    case = data.draw(st.sampled_from(["valid_stream", "arbitrary_input"]))
    bufsize = data.draw(_BUF_SIZES)

    if case == "valid_stream":
        payload = data.draw(st.binary(max_size=4096))
        level = data.draw(st.integers(min_value=0, max_value=9))
        window = data.draw(st.integers(min_value=9, max_value=15))
        larger_or_equal_window = data.draw(st.integers(min_value=window, max_value=15))
        fmt = data.draw(st.sampled_from(["zlib", "raw", "gzip"]))

        if fmt == "zlib":
            compressed = _compress(payload, level, window)
            possible_wbits = [window, larger_or_equal_window, zlib.MAX_WBITS, 32 + larger_or_equal_window]
            if _supports_wbits_zero():
                possible_wbits.append(0)
            decompress_wbits = data.draw(st.sampled_from(possible_wbits))

        elif fmt == "raw":
            compressed = _compress(payload, level, -window)
            decompress_wbits = data.draw(st.sampled_from([-window, -larger_or_equal_window, -zlib.MAX_WBITS]))

        else:
            compressed = _compress(payload, level, 16 + window)
            decompress_wbits = data.draw(
                st.sampled_from([16 + window, 16 + larger_or_equal_window, 16 + zlib.MAX_WBITS, 32 + larger_or_equal_window])
            )

        result = zlib.decompress(compressed, wbits=decompress_wbits, bufsize=bufsize)

        assert isinstance(result, bytes)
        assert result == payload
        assert zlib.decompress(compressed, wbits=decompress_wbits, bufsize=0) == payload
        assert zlib.decompress(compressed, wbits=decompress_wbits, bufsize=65536) == payload

    else:
        raw_input = data.draw(st.binary(max_size=512))
        wbits = data.draw(st.sampled_from(_DOCUMENTED_WBITS))
        other_bufsize = data.draw(_BUF_SIZES)

        try:
            result = zlib.decompress(raw_input, wbits=wbits, bufsize=bufsize)
        except zlib.error:
            return

        assert isinstance(result, bytes)
        assert zlib.decompress(raw_input, wbits=wbits, bufsize=other_bufsize) == result

# End program