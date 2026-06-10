from hypothesis import given, strategies as st
import statistics

# Summary: Generates lists of varying lengths with numeric and non-numeric types, including empty lists.
@given(st.lists(elements=st.one_of(st.integers(), st.floats(), st.text()), min_size=0))
def test_statistics_median(data):
    # Check for TypeError with non-numeric data
    if not all(isinstance(x, (int, float)) for x in data):
        with pytest.raises(TypeError):
            statistics.median(data)
    else:
        # Check for StatisticsError with empty list
        if not data:
            with pytest.raises(statistics.StatisticsError):
                statistics.median(data)
        else:
            # Calculate median and compare with expected result
            expected_median = sorted(data)[len(data) // 2] if len(data) % 2 else (sorted(data)[len(data) // 2 - 1] + sorted(data)[len(data) // 2]) / 2
            assert statistics.median(data) == expected_median, f"Incorrect median for data: {data}"
# End program