from hypothesis import given, strategies as st
import statistics

# Summary: Generate diverse lists of numeric data and test correlation behavior
@given(
    data=st.data(),
    method=st.sampled_from(["linear", "ranked"]),
)
def test_statistics_correlation(data, method):
    # Generate lists of integers and floats with varying lengths
    x = data.draw(
        st.lists(st.one_of(st.integers(), st.floats()), min_size=1)
    )
    y = data.draw(
        st.lists(
            st.one_of(st.integers(), st.floats()), min_size=1, max_size=len(x)
        )
    )

    # Test correlation calculation and error handling
    try:
        result = statistics.correlation(x, y, method=method)
        assert isinstance(result, float)
        assert -1 <= result <= 1
    except statistics.StatisticsError:
        assert len(x) != len(y) or len(x) < 2

# End program