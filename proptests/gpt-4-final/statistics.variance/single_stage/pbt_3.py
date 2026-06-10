from hypothesis import given, strategies as st
from statistics import variance, StatisticsError

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2, max_size=100), st.data())
def test_statistics_variance(data_list, data):

    # calculating the mean of data_list
    mean = sum(data_list) / len(data_list)
 
    # generating either None or calculated mean
    xbar_or_none = data.draw(st.one_of(st.none(), st.just(mean)))
 
    # testing variance calculation
    calculated_variance = variance(data_list, xbar_or_none)

    assert calculated_variance >= 0, "Variance must always be non-negative"
    
    # testing edge cases
    if len(set(data_list)) == 1: 
        assert calculated_variance == 0, "Variance of same numbers must be zero"
       
    # checking for StatisticsError
    with raises(StatisticsError):
        variance([], xbar_or_none)

    with raises(StatisticsError):
        variance([1], xbar_or_none)
# End program