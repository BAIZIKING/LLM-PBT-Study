from hypothesis import given, strategies as st
import zlib

# Summary: Generate lists of byte chunks including empty data, random bytes, repeated 0x00/0xff patterns, and all byte values; also generate valid unsigned 32-bit starting values. Check unsigned result range, determinism, default seed behavior, and running-checksum equivalence over concatenated chunks.
@given(st.data())
def test_zlib_adler32(data):
    chunk_strategy = st.one_of(
        st.binary(min_size=0, max_size=1024),
        st.just(b""),
        st.builds(lambda n: b"\x00" * n, st.integers(min_value=0, max_value=1024)),
        st.builds(lambda n: b"\xff" * n, st.integers(min_value=0, max_value=1024)),
        st.just(bytes(range(256))),
    )

    chunks = data.draw(
        st.lists(chunk_strategy, min_size=1, max_size=8),
        label="chunks",
    )
    initial_value = data.draw(
        st.integers(min_value=0, max_value=0xFFFFFFFF),
        label="initial_value",
    )

    payload = b"".join(chunks)
    payload_object = data.draw(
        st.sampled_from([bytes(payload), bytearray(payload), memoryview(payload)]),
        label="payload_object",
    )

    result = zlib.adler32(payload_object, initial_value)

    assert isinstance(result, int)
    assert 0 <= result <= 0xFFFFFFFF
    assert result == zlib.adler32(payload_object, initial_value)
    assert zlib.adler32(payload_object) == zlib.adler32(payload_object, 1)

    running = initial_value
    for chunk in chunks:
        running = zlib.adler32(chunk, running)

    assert result == running
# End program