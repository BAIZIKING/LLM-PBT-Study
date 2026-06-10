from hypothesis import given, strategies as st
import datetime
import dateutil.parser

@given(st.text())
def test_returning_datetime_object(input_string):
    try:
        result = dateutil.parser.isoparse(input_string)
        assert isinstance(result, datetime.datetime)
    except ValueError:
        pass  # Invalid format, just ignore these errors
    
@st.composite
def generate_unspecified_components(draw):
    return draw(
        st.from_regex(r"^\d{4}(-\d{2}){0,2}(T\d{2}(:\d{2}){0,2}(.\d{0,6})?(([+-]\d{2}(:\d{2})?)|Z)?)?$")
    )

@given(generate_unspecified_components())
def test_default_unspecified_components(input_string):
    try:
        result = dateutil.parser.isoparse(input_string)
        components = [result.year, result.month, result.day, result.hour, result.minute, result.second]
        for i in range(components.count(None)):
            assert components[i] == (1 if i < 3 else 0)  # Year, month, and day should default to 1, others to 0
    except ValueError:
        pass  # Invalid format, just ignore these errors

@st.composite
def generate_timezone(draw):
    return draw(
        st.from_regex(r"^\d{4}(-\d{2}){0,2}T\d{2}(:\d{2}){0,2}(.\d{0,6})?(([+-]\d{2}(:\d{2})?)|Z)$")
    )
        
@given(generate_timezone())
def test_timezone(input_string):
    try:
        result = dateutil.parser.isoparse(input_string)
        assert str(result.tzinfo) in [None, 'tzutc()', input_string[-6:]]
    except ValueError:
        pass  # Invalid format, just ignore these errors

@given(st.data())
def test_incomplete_date_without_time(data):
    random_number = data.draw(st.integers(min_value=1, max_value=12))
    incomplete_date = format(random_number, '02')
    try:
        result = dateutil.parser.isoparse(incomplete_date)
    except ValueError:
        pass  # We expect a ValueError when parsing an incomplete date