@given(
    st.dates(),
    st.dates(
        min_value=datetime.date.min,
        max_value=datetime.date.max,
        # Constrain the second date to be within the same week as the first
        offset_days=st.integers(min_value=-6, max_value=6),
    ),
)
def test_same_iso_week(date1, date2):
    result1 = date1.isocalendar()
    result2 = date2.isocalendar()
    assert result1.year == result2.year
    assert result1.week == result2.week
# End program