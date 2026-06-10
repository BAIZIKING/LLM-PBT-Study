from hypothesis import given, strategies as st
import datetime

@given(st.integers(min_value=1, max_value=9999), 
	   st.integers(min_value=1, max_value=12), 
	   st.integers(min_value=1, max_value=31))
def test_date_isocalendar_year_type(first_input, second_input, third_input):
    try: 
        iso_calendar_date = datetime.date(first_input, second_input, third_input).isocalendar()
        assert isinstance(iso_calendar_date.year, int)
    except ValueError:
        pass


@given(st.integers(min_value=1, max_value=9999), 
	   st.integers(min_value=1, max_value=12), 
	   st.integers(min_value=1, max_value=31))
def test_date_isocalendar_week_range(first_input, second_input, third_input):
    try: 
        iso_calendar_date = datetime.date(first_input, second_input, third_input).isocalendar()
        assert 1 <= iso_calendar_date.week <= 53
    except ValueError:
        pass


@given(st.integers(min_value=1, max_value=9999), 
	   st.integers(min_value=1, max_value=12), 
	   st.integers(min_value=1, max_value=31))
def test_date_isocalendar_weekday_range(first_input, second_input, third_input):
    try: 
        iso_calendar_date = datetime.date(first_input, second_input, third_input).isocalendar()
        assert 1 <= iso_calendar_date.weekday <= 7
    except ValueError:
        pass


@given(st.integers(min_value=1, max_value=9999), 
	   st.integers(min_value=1, max_value=12), 
	   st.integers(min_value=1, max_value=31))
def test_date_isocalendar_deterministic(first_input, second_input, third_input):
    try: 
        iso_calendar_date_1 = datetime.date(first_input, second_input, third_input).isocalendar()
        iso_calendar_date_2 = datetime.date(first_input, second_input, third_input).isocalendar()
        assert iso_calendar_date_1 == iso_calendar_date_2
    except ValueError:
        pass
    

@given(st.integers(min_value=1, max_value=9999), 
	   st.integers(min_value=1, max_value=12), 
	   st.integers(min_value=1, max_value=31))
def test_date_isocalendar_year_displacement(first_input, second_input, third_input):
    try: 
        iso_calendar_date = datetime.date(first_input, second_input, third_input).isocalendar()
        assert first_input - 1 <= iso_calendar_date.year <= first_input + 1
    except ValueError:
        pass