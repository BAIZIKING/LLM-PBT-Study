from hypothesis import given, strategies as st
from statistics import StatisticsError, median
from fractions import Fraction

# Summary: Generate homogeneous numeric inputs as lists of ints, finite floats, or Fractions, including empty inputs, singletons, even/odd lengths, duplicates, zeros, negatives, and large/small values. Randomly pass the same data as a list, tuple, or one-shot iterator to cover both sequence and iterable inputs. Check that empty data raises StatisticsError; otherwise, for odd-length data median returns the sorted middle value, and for even-length data it returns the mean of the two sorted middle values.
@given(st.data())
def test_statistics_median(data):
    values = data.draw(
        st.one_of(
            st.lists(
                st.integers(min_value=-(10**12), max_value=10**12),
                max_size=100,
            ),
            st.lists(
                st.floats(allow_nan=False, allow_infinity=False, width=64),
                max_size=100,
            ),
            st.lists(
                st.fractions(
                    min_value=Fraction(-(10**6)),
                    max_value=Fraction(10**6),
                    max_denominator=10**6,
                ),
                max_size=100,
            ),
        )
    )

    container_type = data.draw(st.sampled_from(["list", "tuple", "iterator"]))
    if container_type == "list":
        input_data = list(values)
    elif container_type == "tuple":
        input_data = tuple(values)
    else:
        input_data = iter(values)

    if not values:
        try:
            median(input_data)
        except StatisticsError:
            return
        raise AssertionError("median() should raise StatisticsError for empty data")

    ordered = sorted(values)
    n = len(ordered)
    mid = n // 2

    if n % 2 == 1:
        expected = ordered[mid]
    else:
        expected = (ordered[mid - 1] + ordered[mid]) / 2

    assert median(input_data) == expected
# End program