from hypothesis import given, strategies as st
import statistics

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2).flatmap(lambda l: st.tuples(st.just(l), st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=len(l), max_size=len(l)))), st.booleans())
def test_linear_regression(input_lists, proportional):
    x, y = input_lists

    # Ensure x is not constant
    if len(set(x)) < 2:
        x[-1] = x[-2] + 1 if x[-2] + 1 != x[-1] else x[-2] - 1

    result = statistics.linear_regression(x, y, proportional=proportional)

    # Check if the result is a tuple
    assert isinstance(result, tuple)

    # Check if the size of the result tuple is 2
    assert len(result) == 2

    # If proportional is True, the intercept should be 0.0
    if proportional:
        assert result[1] == 0.0
# End program