from hypothesis import given, strategies as st
import statistics

# Summary: Generate sequences of various numeric types, including empty sequences, 
# single-element sequences, and sequences with multiple elements (including outliers).
@given(st.data())
def test_statistics_mean(data):
    # Generate a sequence of numeric data with varying types and lengths.
    sequence = data.draw(
        st.lists(
            st.one_of(
                st.integers(),
                st.floats(allow_nan=False, allow_infinity=False),
                st.decimals(),
                st.fractions(),
            ),
            min_size=0,  # Allow empty sequences
        )
    )

    if not sequence:
        # Check if empty sequence raises StatisticsError
        with pytest.raises(statistics.StatisticsError):
            statistics.mean(sequence)
    elif len(sequence) == 1:
        # Check if single-element sequence returns the element itself
        assert statistics.mean(sequence) == sequence[0]
    else:
        # Calculate expected mean and compare with statistics.mean result
        expected_mean = sum(sequence) / len(sequence)
        assert statistics.mean(sequence) == expected_mean

# End program