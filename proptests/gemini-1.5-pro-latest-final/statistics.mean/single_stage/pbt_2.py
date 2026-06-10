from hypothesis import given, strategies as st
from statistics import mean, StatisticsError

# Summary: Generates diverse sequences of numeric data types and tests properties of statistics.mean
@given(st.data())
def test_statistics_mean(data):
    # Generate sequences of different numeric types and sizes
    sequence = data.draw(
        st.one_of(
            st.lists(st.integers()),
            st.lists(st.floats()),
            st.lists(st.fractions()),
            st.lists(st.decimals()),
            st.tuples(st.integers()),
            st.tuples(st.floats()),
            st.tuples(st.fractions()),
            st.tuples(st.decimals()),
        )
    )

    # Test empty sequence
    if not sequence:
        with pytest.raises(StatisticsError):
            mean(sequence)
        return

    # Test single element sequence
    if len(sequence) == 1:
        assert mean(sequence) == sequence[0]
        return

    # Test mean calculation and data type preservation
    calculated_mean = sum(sequence) / len(sequence)
    assert mean(sequence) == calculated_mean
    assert type(mean(sequence)) == type(calculated_mean)

# End program