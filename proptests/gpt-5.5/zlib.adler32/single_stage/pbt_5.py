from hypothesis import given, strategies as st
import zlib

# Summary: Generate lists of byte chunks including empty data, arbitrary bytes, repeated NUL bytes,
# repeated 0xff bytes, and varied lengths; generate starting checksum values across the full
# unsigned 32-bit range with boundary cases. Check that results are unsigned 32-bit integers,
# that omitting value is equivalent to value=1, and that incremental checksumming over chunks
# equals checksumming their concatenation.
@given(st.data())
def test_zlib_adler32(data):
    chunk_strategy = st.one_of(
        st.just(b""),
        st.just(b"\x00"),
        st.just(b"\xff"),
        st.binary(min_size=0, max_size=2048),
        st.integers(min_value=0, max_value=2048).map(lambda n: b"\x00" * n),
        st.integers(min_value=0, max_value=2048).map(lambda n: b"\xff" * n),
    )

    chunks = data.draw(st.lists(chunk_strategy, min_size=0, max_size=20))
    payload = b"".join(chunks)

    start_value = data.draw(
        st.one_of(
            st.sampled_from([0, 1, 65521, 0x7FFFFFFF, 0x80000000, 0xFFFFFFFF]),
            st.integers(min_value=0, max_value=0xFFFFFFFF),
        )
    )

    result = zlib.adler32(payload, start_value)

    assert isinstance(result, int)
    assert 0 <= result <= 0xFFFFFFFF

    assert zlib.adler32(payload) == zlib.adler32(payload, 1)

    running = start_value
    for chunk in chunks:
        running = zlib.adler32(chunk, running)

    assert running == zlib.adler32(payload, start_value)

# End program