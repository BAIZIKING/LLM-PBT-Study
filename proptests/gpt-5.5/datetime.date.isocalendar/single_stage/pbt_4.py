from hypothesis import given, strategies as st
from datetime import date, timedelta

# Summary: Generate a date from a mix of arbitrary valid datetime.date values and
# targeted edge cases: date.min/date.max, leap-day dates, Gregorian year boundaries,
# documented ISO boundary examples, and known 52/53-week ISO year transitions.
# Check that isocalendar() returns named fields, valid ISO ranges, Monday=1 weekday
# numbering, and that the ISO year/week independently match the rule that an ISO
# week starts on Monday and belongs to the Gregorian year of its Thursday.
@given(st.data())
def test_datetime_date_isocalendar(data):
    edge_dates = [
        date.min,
        date.max,
        date(1, 1, 1),
        date(2000, 2, 29),
        date(1900, 2, 28),
        date(2003, 12, 29),
        date(2004, 1, 1),
        date(2004, 1, 4),
        date(2004, 12, 31),
        date(2005, 1, 1),
        date(2009, 12, 31),
        date(2010, 1, 1),
        date(2015, 12, 31),
        date(2016, 1, 1),
        date(2020, 12, 31),
        date(2021, 1, 1),
    ]

    d = data.draw(
        st.one_of(
            st.dates(min_value=date.min, max_value=date.max),
            st.sampled_from(edge_dates),
        )
    )

    iso = d.isocalendar()

    assert hasattr(iso, "year")
    assert hasattr(iso, "week")
    assert hasattr(iso, "weekday")
    assert tuple(iso) == (iso.year, iso.week, iso.weekday)

    assert 1 <= iso.week <= 53
    assert 1 <= iso.weekday <= 7

    assert iso.weekday == d.weekday() + 1

    week_monday = d - timedelta(days=iso.weekday - 1)
    week_thursday = week_monday + timedelta(days=3)

    assert week_monday.weekday() == 0
    assert week_thursday.year == iso.year

    first_week_monday = date(iso.year, 1, 4) - timedelta(
        days=date(iso.year, 1, 4).weekday()
    )

    assert week_monday == first_week_monday + timedelta(weeks=iso.week - 1)

    if iso.year < date.max.year:
        next_year_first_week_monday = date(iso.year + 1, 1, 4) - timedelta(
            days=date(iso.year + 1, 1, 4).weekday()
        )
        weeks_in_iso_year = (
            next_year_first_week_monday - first_week_monday
        ).days // 7

        assert weeks_in_iso_year in (52, 53)
        assert iso.week <= weeks_in_iso_year

# End program