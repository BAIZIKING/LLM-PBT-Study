from hypothesis import given, strategies as st
import datetime

@given(st.data())
def test_datetime_date_isocalendar_property(data):
    d = data.draw(
        st.dates(
            min_value=datetime.date.min,
            max_value=datetime.date.max,
        )
    )

    iso = d.isocalendar()

    assert len(iso) == 3
    assert hasattr(iso, "year")
    assert hasattr(iso, "week")
    assert hasattr(iso, "weekday")
    assert tuple(iso) == (iso.year, iso.week, iso.weekday)

    assert isinstance(iso.weekday, int)
    assert 1 <= iso.weekday <= 7
    assert iso.weekday == d.weekday() + 1

    assert isinstance(iso.week, int)
    assert 1 <= iso.week <= 53

    ordinal = d.toordinal()
    week_start_ordinal = ordinal - (iso.weekday - 1)
    week_end_ordinal = week_start_ordinal + 6

    assert week_start_ordinal <= ordinal <= week_end_ordinal
    assert ((week_start_ordinal - 1) % 7) + 1 == 1
    assert ((week_end_ordinal - 1) % 7) + 1 == 7

    thursday_ordinal = ordinal + (4 - iso.weekday)
    assert datetime.date.min.toordinal() <= thursday_ordinal <= datetime.date.max.toordinal()

    thursday = datetime.date.fromordinal(thursday_ordinal)
    assert iso.year == thursday.year

# End program