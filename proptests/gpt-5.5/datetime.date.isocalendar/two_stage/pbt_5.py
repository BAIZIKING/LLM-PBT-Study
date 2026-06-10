from hypothesis import given, strategies as st
import datetime

date_strategy = st.dates(
    min_value=datetime.date.min,
    max_value=datetime.date.max,
)


@given(st.data())
def test_datetime_date_isocalendar_has_named_components(data):
    d = data.draw(date_strategy)
    result = d.isocalendar()

    assert len(result) == 3
    assert hasattr(result, "year")
    assert hasattr(result, "week")
    assert hasattr(result, "weekday")
    assert result.year == result[0]
    assert result.week == result[1]
    assert result.weekday == result[2]


@given(st.data())
def test_datetime_date_isocalendar_weekday_range(data):
    d = data.draw(date_strategy)
    result = d.isocalendar()

    assert 1 <= result.weekday <= 7
    assert result.weekday == d.weekday() + 1


@given(st.data())
def test_datetime_date_isocalendar_week_range(data):
    d = data.draw(date_strategy)
    result = d.isocalendar()

    assert 1 <= result.week <= 53


@given(st.data())
def test_datetime_date_isocalendar_same_week_monday_to_sunday(data):
    max_safe_ordinal = datetime.date.max.toordinal() - 6
    ordinal = data.draw(
        st.integers(
            min_value=datetime.date.min.toordinal(),
            max_value=max_safe_ordinal,
        )
    )
    d = datetime.date.fromordinal(ordinal)

    result = d.isocalendar()
    monday = d - datetime.timedelta(days=result.weekday - 1)
    monday_result = monday.isocalendar()
    expected_year = monday_result.year
    expected_week = monday_result.week

    for offset in range(7):
        current = monday + datetime.timedelta(days=offset)
        current_result = current.isocalendar()

        assert current_result.year == expected_year
        assert current_result.week == expected_week
        assert current_result.weekday == offset + 1


@given(st.data())
def test_datetime_date_isocalendar_iso_year_rule(data):
    d = data.draw(date_strategy)
    result = d.isocalendar()

    if 2 <= d.month <= 11:
        assert result.year == d.year

    thursday_of_iso_week = d + datetime.timedelta(days=4 - result.weekday)
    assert result.year == thursday_of_iso_week.year


# End program