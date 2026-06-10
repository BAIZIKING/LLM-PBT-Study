from hypothesis import given, strategies as st
import datetime
import math

# Strategy for timedeltas that avoids overflow and the >270 year microsecond
# accuracy loss noted in the documentation. We restrict the range so that
# arithmetic (multiplication, addition) stays within timedelta.min/max bounds
# and microsecond precision is preserved.
safe_timedeltas = st.timedeltas(
    min_value=datetime.timedelta(days=-100 * 365),
    max_value=datetime.timedelta(days=100 * 365),
)


@given(td=safe_timedeltas)
def test_datetime_timedelta_total_seconds_type_and_finiteness(td):
    result = td.total_seconds()
    assert isinstance(result, float)
    assert math.isfinite(result)
# End program


@given(td=safe_timedeltas)
def test_datetime_timedelta_total_seconds_equivalence_to_division(td):
    result = td.total_seconds()
    assert result == td / datetime.timedelta(seconds=1)
# End program


@given(td=safe_timedeltas)
def test_datetime_timedelta_total_seconds_component_consistency(td):
    result = td.total_seconds()
    expected = td.days * 86400 + td.seconds + td.microseconds / 1_000_000
    assert math.isclose(result, expected, rel_tol=1e-9, abs_tol=1e-6)
# End program


@given(td=safe_timedeltas)
def test_datetime_timedelta_total_seconds_sign_correspondence(td):
    result = td.total_seconds()
    zero = datetime.timedelta(0)
    if td == zero:
        assert result == 0.0
    elif td > zero:
        assert result > 0.0
    else:
        assert result < 0.0
# End program


@given(
    td=st.timedeltas(
        min_value=datetime.timedelta(days=-3 * 365),
        max_value=datetime.timedelta(days=3 * 365),
    ),
    td2=st.timedeltas(
        min_value=datetime.timedelta(days=-3 * 365),
        max_value=datetime.timedelta(days=3 * 365),
    ),
    n=st.integers(min_value=-20, max_value=20),
)
def test_datetime_timedelta_total_seconds_linearity(td, td2, n):
    # Scaling
    scaled = (n * td).total_seconds()
    assert math.isclose(scaled, n * td.total_seconds(), rel_tol=1e-9, abs_tol=1e-6)
    # Additivity
    summed = (td + td2).total_seconds()
    assert math.isclose(
        summed,
        td.total_seconds() + td2.total_seconds(),
        rel_tol=1e-9,
        abs_tol=1e-6,
    )
# End program