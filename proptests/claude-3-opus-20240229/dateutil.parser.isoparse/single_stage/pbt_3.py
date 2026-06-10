from hypothesis import given, strategies as st
from dateutil.parser import isoparse
from datetime import datetime, timezone

# Summary: 
# Generate a variety of valid ISO 8601 datetime strings, including:
# - Dates with different precisions (YYYY, YYYY-MM, YYYY-MM-DD)
# - Dates with ISO week format 
# - Times with different precisions (hh, hh:mm, hh:mm:ss, hh:mm:ss.ssssss)
# - Times with either dot or comma decimal separator
# - Midnight represented as both 00:00 and 24:00
# - Various timezone offsets (Z, ±HH:MM, ±HHMM, ±HH)
# Check that isoparse parses the string correctly and returns expected datetime

@given(st.one_of(
    st.dates().map(lambda d: d.strftime('%Y-%m-%d')),  # YYYY-MM-DD   
    st.dates().map(lambda d: d.strftime('%Y%m%d')),    # YYYYMMDD
    st.dates().map(lambda d: d.strftime('%Y-%m')),     # YYYY-MM
    st.dates().map(lambda d: d.strftime('%Y%m')),      # YYYYMM  
    st.dates().map(lambda d: d.strftime('%Y-W%W-%w')), # YYYY-Www-D
    st.dates().map(lambda d: d.strftime('%YW%W%w')),   # YYYYWwwD
    st.dates().map(lambda d: d.strftime('%Y-W%W')),    # YYYY-Www  
    st.dates().map(lambda d: d.strftime('%YW%W')),     # YYYYWww
    st.dates().map(lambda d: d.strftime('%Y')),        # YYYY
).flatmap(lambda d: st.one_of(
    st.just(d),
    st.just(d+'T00'),
    st.just(d+'T00:00'), 
    st.just(d+'T24:00'),
    st.just(d+'T00:00:00'),
    st.just(d+'T00:00:00.0'),
    st.just(d+'T00:00:00.00'),
    st.just(d+'T00:00:00.000000'),
    st.just(d+'T00:00:00,000000'),
    st.just(d+'T00Z'),
    st.just(d+'T00:00Z'),
    st.just(d+'T00:00:00Z'),  
    st.just(d+'T00:00:00-01:23'),
    st.just(d+'T00:00:00-0123'),
    st.just(d+'T00:00:00+02'),    
)))
def test_isoparse(dt_str):
    dt = isoparse(dt_str)
    assert type(dt) is datetime
    if 'Z' in dt_str:
        assert dt.tzinfo is timezone.utc
    elif '-' in dt_str or '+' in dt_str:
        assert dt.tzinfo is not None
    else:
        assert dt.tzinfo is None
        
    for fmt in ('%Y-%m-%d', '%Y%m%d', '%Y-%m', '%Y%m', '%Y-W%W-%w', 
                '%YW%W%w', '%Y-W%W', '%YW%W', '%Y'):
        if dt_str.startswith(datetime.strptime(dt_str.split('T')[0], fmt).strftime(fmt)):
            assert dt == datetime.strptime(dt_str.split('.')[0].replace(',','.'), fmt+'T%H:%M:%S.%f%z')
            break
# End program