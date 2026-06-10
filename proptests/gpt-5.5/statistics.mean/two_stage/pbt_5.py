from hypothesis import given, strategies as st
import statistics

@given(st.data())
def test_statistics_mean_property(data):
    def close(a, b):
        return abs(a - b) <= 1e-7 * max(1.0, abs(a), abs(b))

    bounded_floats = st.floats(
        min_value=-1_000_000,
        max_value=1_000_000,
        allow_nan=False,
        allow_infinity=False,
        width=32,
    )

    # Property 1: mean equals sum(data) / len(data) for non-empty numeric data.
    xs = data.draw(st.lists(bounded_floats, min_size=1, max_size=100))
    assert close(statistics.mean(xs), sum(xs) / len(xs))

    # Property 2: permuting the data does not change the mean.
    xs = data.draw(st.lists(bounded_floats, min_size=1, max_size=100))
    assert close(statistics.mean(xs), statistics.mean(list(reversed(xs))))

    # Property 3: if all input values are the same value x, the mean is x.
    x = data.draw(st.integers(min_value=-1_000_000, max_value=1_000_000))
    n = data.draw(st.integers(min_value=1, max_value=100))
    assert statistics.mean([x] * n) == x

    # Property 4: the mean lies between the minimum and maximum input values.
    xs = data.draw(st.lists(bounded_floats, min_size=1, max_size=100))
    result = statistics.mean(xs)
    assert min(xs) - 1e-7 <= result <= max(xs) + 1e-7

    # Property 5: translating and scaling all values translates and scales the mean.
    xs = data.draw(
        st.lists(
            st.integers(min_value=-10_000, max_value=10_000),
            min_size=1,
            max_size=100,
        )
    )
    c = data.draw(st.integers(min_value=-10_000, max_value=10_000))
    k = data.draw(st.integers(min_value=-100, max_value=100))

    base_mean = statistics.mean(xs)

    translated = [value + c for value in xs]
    assert close(statistics.mean(translated), base_mean + c)

    scaled = [k * value for value in xs]
    assert close(statistics.mean(scaled), k * base_mean)
# End program