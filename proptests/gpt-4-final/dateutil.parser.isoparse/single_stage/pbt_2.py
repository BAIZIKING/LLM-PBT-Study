from hypothesis import given, strategies as st
from hypothesis.strategies import drawn_from
from dateutil.parser import isoparse

time_formats = drawn_from(['hh', 'hhmm', 'hh:mm', 'hh:mm:ss', 'hhmmss', 'hh:mm:ss.ssssss'])
date_formats = drawn_from(['YYYY', 'YYYYMM', 'YYYY-MM', 'YYYYMMDD', 'YYYY-MM-DD', 
                           'YYYYWww', 'YYYY-Www', 'YYYYWwwD', 'YYYY-Www-D'])
offset_formats = drawn_from(['Z', '±HH:MM', '±HHMM', '±HH'])

def generate_date(format):
    if format in ['YYYY', 'YYYY-Www-D', 'YYYYWwwD']:
        return st.dates().map(lambda x: x.strftime(format))
    else:
        return st.datetimes().map(lambda x: x.strftime(format))
        
def generate_time(format):
    return st.times().map(lambda x: x.strftime(format))
    
def generate_offset(format):
    if format == 'Z':
        return st.just('Z')
    else:
        return st.timezones().map(lambda x: x.strftime(format))

@given(date=st.builds(generate_date, date_formats), time=st.builds(generate_time, time_formats), 
       offset=st.builds(generate_offset, offset_formats))
def test_isoparse(date, time, offset):
    date_str = f'{date}T{time}{offset}'
    try:
        isoparse(date_str)
    except Exception as e:
        assert False, f'input was \"{date_str}\" isoparse threw \"{str(e)}\"' 
# End program