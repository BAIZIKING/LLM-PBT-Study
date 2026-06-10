@given(timedelta_strategy, timedelta_strategy)
def test_timedelta_total_seconds_comparison_consistency(td1, td2):
    comparison_result = td1 > td2
    seconds_comparison = td1.total_seconds() > td2.total_seconds()
    assert comparison_result == seconds_comparison
# End program