from hypothesis import given, strategies as st
import datetime

# Strategy for generating timedeltas, bounded to avoid microsecond-precision
# loss noted in the docs (intervals > ~270 years lose accuracy).
# datetime.timedelta supports roughly +/- 999999999 days, but we restrict
# the range to stay within safe float precision for these tests.
safe_timedeltas = st.timedeltas(
    min_value=datetime.timedelta(days=-100 * 365),
    max_value=datetime.timedelta(days=100 * 365),
)


@given(td=safe_timedeltas)
def test_datetime_timedelta_total_seconds_type_is_float(td):
    # Property 1: The output is always a float.
    result = td.total_seconds()
    assert isinstance(result, float)
# End program


@given(td=safe_timedeltas)
def test_datetime_timedelta_total_seconds_equals_division(td):
    # Property 2: Output equals td / timedelta(seconds=1).
    result = td.total_seconds()
    expected = td / datetime.timedelta(seconds=1)
    assert result == expected
# End program


@given(td=safe_timedeltas)
def test_datetime_timedelta_total_seconds_sign_correspondence(td):
    # Property 3: Sign of output matches sign of the timedelta.
    result = td.total_seconds()
    zero = datetime.timedelta(0)
    if td > zero:
        assert result > 0
    elif td < zero:
        assert result < 0
    else:
        assert result == 0.0
# End program


@given(td=safe_timedeltas)
def test_datetime_timedelta_total_seconds_component_reconstruction(td):
    # Property 4: Output equals days*86400 + seconds + microseconds/1e6.
    result = td.total_seconds()
    expected = td.days * 86400 + td.seconds + td.microseconds / 1_000_000
    assert result == expected
# End program


@given(td=safe_timedeltas)
def test_datetime_timedelta_total_seconds_negation_symmetry(td):
    # Property 5: Negating the timedelta negates the output.
    result = (-td).total_seconds()
    expected = -td.total_seconds()
    assert result == expected
# End program