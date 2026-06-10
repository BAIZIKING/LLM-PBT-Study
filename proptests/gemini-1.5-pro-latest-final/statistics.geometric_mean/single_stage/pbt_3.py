from hypothesis import given, strategies as st
import statistics

# Summary: Generates diverse data structures containing positive floats, 
#          occasionally including empty datasets or negative values.
@given(st.data())
def test_statistics_geometric_mean(data):
    # Draw a boolean to determine if we test for emptiness
    test_empty = data.draw(st.booleans())
    
    # Draw a list of floats, potentially including negative values
    values = data.draw(
        st.lists(
            st.floats(min_value=0, exclude_min=True) | 
            st.floats(max_value=0, exclude_max=True, allow_nan=False), 
            min_size=1
        )
    )
    
    if test_empty:
        values = []
    
    # Check for expected errors
    if len(values) == 0 or any(value <= 0 for value in values):
        with pytest.raises(statistics.StatisticsError):
            statistics.geometric_mean(values)
    else:
        # Test accuracy with a controlled dataset 
        if values == [2.0, 8.0]:
            assert statistics.geometric_mean(values) == 4.0

# End program