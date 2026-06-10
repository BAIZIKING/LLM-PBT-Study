from hypothesis import given, strategies as st
import zlib

@given(st.binary(max_size=1024))  # Limit data size to avoid potential overflows
def test_empty_input(data):
    empty_data = b''
    assert zlib.adler32(empty_data) == 1  # Check for expected default value

@given(st.binary(max_size=1024))
def test_order_independence(data):
    shuffled_data = data.copy()
    shuffled_data[:len(data)] = sorted(data)  # Shuffle data
    assert zlib.adler32(data) == zlib.adler32(shuffled_data)

@given(st.binary(max_size=512), st.binary(max_size=512))  # Smaller sizes to avoid exceeding limits
def test_running_checksum(data1, data2):
    combined_data = data1 + data2
    checksum1 = zlib.adler32(data1)
    checksum2 = zlib.adler32(data2, checksum1)
    assert checksum2 == zlib.adler32(combined_data)

@given(st.binary(max_size=1024), st.integers(min_value=1))
def test_initial_value_influence(data, initial_value):
    default_checksum = zlib.adler32(data)
    custom_checksum = zlib.adler32(data, initial_value)
    assert default_checksum != custom_checksum

@given(st.binary(max_size=1024), st.integers(min_value=1))
def test_deterministic_output(data, initial_value):
    first_run = zlib.adler32(data, initial_value)
    second_run = zlib.adler32(data, initial_value)
    assert first_run == second_run
# End program