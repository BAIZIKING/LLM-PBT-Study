from hypothesis import given, strategies as st
import zlib

# Summary: Generate `data` as arbitrary bytes (including empty) and `value` as either
# None (to test default) or an unsigned 32-bit integer covering edge values [0, 2**32-1].
# Also generate a second bytes input to verify the running/concatenation checksum property.
@given(st.data())
def test_zlib_adler32():
    data = st.data().draw  # placeholder to satisfy format; real draws below
    d = st_data = None

    # Draw inputs using the provided data strategy
    import hypothesis
    @given(
        data1=st.binary(min_size=0, max_size=1024),
        data2=st.binary(min_size=0, max_size=1024),
        value=st.one_of(st.none(), st.integers(min_value=0, max_value=2**32 - 1)),
    )
    def inner(data1, data2, value):
        # Property 1: result is always an unsigned 32-bit integer
        if value is None:
            result = zlib.adler32(data1)
        else:
            result = zlib.adler32(data1, value)
        assert isinstance(result, int)
        assert 0 <= result <= 2**32 - 1

        # Property 2: omitting value equals passing default value of 1
        assert zlib.adler32(data1) == zlib.adler32(data1, 1)

        # Property 3: running checksum over concatenation
        # adler32(data1 + data2) == adler32(data2, adler32(data1))
        combined = zlib.adler32(data1 + data2)
        running = zlib.adler32(data2, zlib.adler32(data1))
        assert combined == running

    inner()
# End program