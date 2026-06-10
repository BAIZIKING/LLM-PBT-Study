from hypothesis import given, strategies as st, assume
import statistics
import pytest

safe_floats = st.floats(
    min_value=-1e6,
    max_value=1e6,
    allow_nan=False,
    allow_infinity=False,
)


@given(
    x=st.lists(safe_floats, min_size=0, max_size=50),
    proportional=st.booleans(),
    data=st.data(),
)
def test_raises_statistics_error_on_invalid_input(x, proportional, data):
    # Property 5: StatisticsError raised when inputs too short, length mismatch,
    # or x is constant.
    # Decide which invalid scenario to construct.
    scenario = data.draw(st.sampled_from(["too_short", "mismatch", "constant"]))

    if scenario == "too_short":
        # Use 0 or 1 elements.
        n = data.draw(st.sampled_from([0, 1]))
        xs = data.draw(st.lists(safe_floats, min_size=n, max_size=n))
        ys = data.draw(st.lists(safe_floats, min_size=n, max_size=n))
        with pytest.raises(statistics.StatisticsError):
            statistics.linear_regression(xs, ys, proportional=proportional)

    elif scenario == "mismatch":
        # Different lengths, each at least length 2.
        len_x = data.draw(st.integers(min_value=2, max_value=10))
        len_y = data.draw(st.integers(min_value=2, max_value=10))
        assume(len_x != len_y)
        xs = data.draw(st.lists(safe_floats, min_size=len_x, max_size=len_x))
        ys = data.draw(st.lists(safe_floats, min_size=len_y, max_size=len_y))
        with pytest.raises(statistics.StatisticsError):
            statistics.linear_regression(xs, ys, proportional=proportional)

    else:  # constant x
        n = data.draw(st.integers(min_value=2, max_value=10))
        const = data.draw(safe_floats)
        xs = [const] * n
        ys = data.draw(st.lists(safe_floats, min_size=n, max_size=n))
        with pytest.raises(statistics.StatisticsError):
            statistics.linear_regression(xs, ys, proportional=proportional)
# End program