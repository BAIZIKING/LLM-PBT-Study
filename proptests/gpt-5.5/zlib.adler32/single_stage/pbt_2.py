import zlib
from hypothesis import given, strategies as st

# Summary: Generate byte-oriented inputs using a mix of empty bytes, random bytes,
# repeated-byte patterns, and concatenated chunks; also generate optional Adler-32
# starting values including important edges such as 0, 1, and 2**32 - 1. Check that
# results are unsigned 32-bit integers, that omitting value is equivalent to value=1,
# and that incremental checksum computation matches checksum over concatenated data.
@given(st.data())
def test_zlib_adler32(data):
    payload_strategy = st.one_of(
        st.just(b""),
        st.binary(min_size=0, max_size=4096),
        st.builds(
            lambda byte, count: bytes([byte]) * count,
            st.integers(min_value=0, max_value=255),
            st.integers(min_value=0, max_value=4096),
        ),
        st.lists(
            st.binary(min_size=0, max_size=128),
            min_size=0,
            max_size=32,
        ).map(b"".join),
    )

    start_value_strategy = st.one_of(
        st.none(),
        st.sampled_from([0, 1, 2**16 - 1, 2**16, 2**31, 2**32 - 1]),
        st.integers(min_value=0, max_value=2**32 - 1),
    )

    payload = data.draw(payload_strategy)
    start_value = data.draw(start_value_strategy)

    if start_value is None:
        result = zlib.adler32(payload)
        effective_start_value = 1

        # Omitting value must be equivalent to using the documented default value 1.
        assert result == zlib.adler32(payload, 1)
    else:
        result = zlib.adler32(payload, start_value)
        effective_start_value = start_value

    # The documented result is always an unsigned 32-bit integer.
    assert isinstance(result, int)
    assert 0 <= result <= 2**32 - 1

    split_index = data.draw(st.integers(min_value=0, max_value=len(payload)))
    left = payload[:split_index]
    right = payload[split_index:]

    # Passing value allows a running checksum over concatenated inputs.
    incremental_result = zlib.adler32(
        right,
        zlib.adler32(left, effective_start_value),
    )
    whole_result = zlib.adler32(payload, effective_start_value)

    assert incremental_result == whole_result == result
# End program