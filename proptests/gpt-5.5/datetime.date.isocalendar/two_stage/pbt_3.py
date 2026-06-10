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

    assert isinstance(iso.year, int)
    assert isinstance(iso.week, int)
    assert isinstance(iso.weekday, int)

    assert 1 <= iso.weekday <= 7
    assert 1 <= iso.week <= 53

    assert iso.weekday == d.weekday() + 1

    assert datetime.date.fromisocalendar(
        iso.year,
        iso.week,
        iso.weekday,
    ) == d

# End program