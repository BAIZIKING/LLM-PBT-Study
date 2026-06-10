from hypothesis import given, strategies as st
import zlib

# Summary: Generate known-valid zlib/raw/gzip streams from varied payloads, levels, and window sizes,
# plus arbitrary byte strings with valid documented wbits values. Exercise edge-ish bufsize values
# because bufsize should only affect allocation, not output. Properties checked: compatible valid
# streams round-trip to the original payload; changing bufsize does not change successful output;
# arbitrary invalid streams may raise zlib.error, as documented.
@given(st.data())
def test_zlib_decompress(data):
    payload_strategy = st.one_of(
        st.sampled_from([
            b"",
            b"\x00",
            b"a",
            b"\x00" * 1024,
            b"abc" * 1000,
            bytes(range(256)),
        ]),
        st.binary(max_size=4096),
        st.builds(
            lambda chunk, count: chunk * count,
            st.binary(min_size=1, max_size=16),
            st.integers(min_value=0, max_value=512),
        ),
    )

    bufsize_for = lambda payload: st.one_of(
        st.sampled_from([
            1,
            2,
            8,
            zlib.DEF_BUF_SIZE,
            max(1, len(payload)),
            max(1, len(payload) + 1),
        ]),
        st.integers(min_value=1, max_value=65536),
    )

    valid_wbits = st.one_of(
        st.integers(min_value=8, max_value=15),
        st.just(0),
        st.integers(min_value=-15, max_value=-8),
        st.integers(min_value=24, max_value=31),
        st.integers(min_value=40, max_value=47),
    )

    scenario = data.draw(st.sampled_from(["valid_zlib", "valid_raw", "valid_gzip", "arbitrary"]))

    if scenario == "arbitrary":
        compressed = data.draw(st.binary(max_size=64))
        wbits = data.draw(valid_wbits)
        bufsize1 = data.draw(st.integers(min_value=1, max_value=65536))
        bufsize2 = data.draw(st.integers(min_value=1, max_value=65536))

        try:
            result1 = zlib.decompress(compressed, wbits=wbits, bufsize=bufsize1)
        except zlib.error:
            return

        result2 = zlib.decompress(compressed, wbits=wbits, bufsize=bufsize2)
        assert isinstance(result1, bytes)
        assert result1 == result2
        return

    payload = data.draw(payload_strategy)
    level = data.draw(st.integers(min_value=0, max_value=9))
    compress_window = data.draw(st.integers(min_value=9, max_value=15))

    if scenario == "valid_zlib":
        compressor_wbits = compress_window
        compatible_wbits = (
            list(range(compress_window, 16))
            + [0]
            + [32 + n for n in range(compress_window, 16)]
        )
    elif scenario == "valid_raw":
        compressor_wbits = -compress_window
        compatible_wbits = [-n for n in range(compress_window, 16)]
    else:
        compressor_wbits = 16 + compress_window
        compatible_wbits = (
            [16 + n for n in range(compress_window, 16)]
            + [32 + n for n in range(compress_window, 16)]
        )

    compressor = zlib.compressobj(level=level, wbits=compressor_wbits)
    compressed = compressor.compress(payload) + compressor.flush()

    wbits = data.draw(st.sampled_from(compatible_wbits))
    bufsize1 = data.draw(bufsize_for(payload))
    bufsize2 = data.draw(bufsize_for(payload))

    result1 = zlib.decompress(compressed, wbits=wbits, bufsize=bufsize1)
    result2 = zlib.decompress(compressed, wbits=wbits, bufsize=bufsize2)

    assert result1 == payload
    assert result2 == payload
    assert result1 == result2
# End program