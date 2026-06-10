from hypothesis import given, strategies as st

# Strategy for generating datetimes with varying microsecond precision
datetime_strategy_varying_us = st.builds(
    lambda y, m, d, h, min, s, us: f"{y:04}-{m:02}-{d:02}T{h:02}:{min:02}:{s:02}.{us}",
    year_strategy, month_strategy, day_strategy, hour_strategy, minute_strategy,
    second_strategy, st.text(alphabet=st.digits(), min_size=1, max_size=6)  # Varying length of microseconds
)

@given(datetime_strategy_varying_us)
def test_dateutil_parser_isoparse_microsecond_precision(dt_str):
    parsed_datetime = dateutil.parser.isoparse(dt_str)
    assert 0 <= parsed_datetime.microsecond <= 999999 
# End program