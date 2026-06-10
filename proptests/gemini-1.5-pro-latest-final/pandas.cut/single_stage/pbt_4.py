from hypothesis import given, strategies as st
import pandas as pd


# Summary: This strategy generates diverse inputs for pandas.cut, including:
# - x: array-like input with various data types and lengths
# - bins: different binning criteria (int, sequence, IntervalIndex)
# - right: True or False
# - labels: optional labels for bins
# - retbins: True or False
# - precision: integer precision for bin labels
# - include_lowest: True or False
# - duplicates: 'raise' or 'drop'
# - ordered: True or False
@given(st.data())
def test_pandas_cut(data):
    # Generate input data
    x = data.draw(
        st.one_of(
            st.lists(st.floats()),
            st.lists(st.integers()),
            st.lists(st.datetimes()),
        )
    )

    # Generate binning criteria
    bins = data.draw(
        st.one_of(
            st.integers(min_value=1),
            st.lists(st.floats(allow_nan=False)),
            st.builds(pd.IntervalIndex.from_tuples, st.lists(st.tuples(st.floats(), st.floats()))),
        )
    )

    # Generate other parameters
    right = data.draw(st.booleans())
    labels = data.draw(st.one_of(st.none(), st.lists(st.text())))
    retbins = data.draw(st.booleans())
    precision = data.draw(st.integers(min_value=0))
    include_lowest = data.draw(st.booleans())
    duplicates = data.draw(st.sampled_from(["raise", "drop"]))
    ordered = data.draw(st.booleans())

    # Call pandas.cut and handle potential exceptions
    try:
        result = pd.cut(
            x, bins, right=right, labels=labels, retbins=retbins, precision=precision,
            include_lowest=include_lowest, duplicates=duplicates, ordered=ordered
        )
    except ValueError:
        # Ignore cases where bins might be invalid
        return

    # Assertions based on API documentation:
    # 1. Check output type based on labels
    if labels is None:
        if isinstance(x, pd.Series):
            assert isinstance(result, pd.Series)
        else:
            assert isinstance(result, pd.Categorical)
    elif labels is False:
        assert isinstance(result, (np.ndarray, pd.Index))
    else:
        assert isinstance(result, pd.Categorical)

    # 2. Check returned bins when retbins is True
    if retbins:
        if isinstance(bins, int):
            assert isinstance(result[1], np.ndarray)
        else:
            assert isinstance(result[1], pd.IntervalIndex)

    # 3. Check order of categorical data
    if isinstance(result, pd.Categorical):
        if ordered:
            assert result.ordered
        else:
            assert not result.ordered

# End program