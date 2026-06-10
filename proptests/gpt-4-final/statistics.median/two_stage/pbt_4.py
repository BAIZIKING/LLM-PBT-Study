from hypothesis import given, strategies as st, assume
import statistics



#Property 1: The output will always be a number
@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
def test_output_is_number(lst):
    result = statistics.median(lst)
    assert isinstance(result, (int, float))

#Property 2: For a sorted input with an odd number of elements, the output of the median function will equal the middle element of the input array.
@given(st.lists(st.integers(), min_size=3, max_size=9).filter(lambda x: len(x) % 2 == 1))
def test_odd_number_of_elements(lst):
    lst = sorted(lst)
    result = statistics.median(lst)
    expected = lst[len(lst)//2]
    assert result == expected

#Property 3: For a sorted input with an even number of elements, the output of the median function will be the average of the two middle elements.
@given(st.lists(st.integers(), min_size=2, max_size=10).filter(lambda x: len(x) % 2 == 0))
def test_even_number_of_elements(lst):
    lst = sorted(lst)
    result = statistics.median(lst)
    expected = (lst[len(lst)//2 - 1] + lst[len(lst)//2]) / 2
    assert result == expected

#Property 4: The function should raise a StatisticsError for an empty input.
def test_empty_input():
    try:
        statistics.median([])
    except statistics.StatisticsError:
        pass
    else:
        assert False, "Expected StatisticsError"

#Property 5: The function should work the same way for both sequences and iterables.
@given(st.tuples(st.floats(allow_nan=False, allow_infinity=False), st.floats(allow_nan=False, allow_infinity=False), st.floats(allow_nan=False, allow_infinity=False)))
def test_input_types(tple):
    lst = list(tple)
    assert statistics.median(lst) == statistics.median(tple)