from hypothesis import given, strategies as st
import pandas as pd


# Summary: This strategy generates diverse inputs for pandas.cut, including:
# - 1D array-like data (lists) of various numeric types
# - Different binning criteria:
#   - Number of bins (int)
#   - Sequence of scalars (list of floats)
#   - IntervalIndex
# - Different values for right, labels, retbins, precision, include_lowest, duplicates, ordered
@given(st.data())
def test_pandas_cut(data):
    # Generate data
    x = data.draw(
        st.lists(
            st.one_of(st.integers(), st.floats(allow_nan=False)), min_size=1
        )
    )

    # Generate binning criteria
    bins_strategy = st.one_of(
        st.integers(min_value=1),
        st.lists(st.floats(allow_nan=False), min_size=2, unique=True),
        st.builds(
            pd.IntervalIndex.from_tuples,
            st.lists(
                st.tuples(st.floats(), st.floats()), min_size=2, unique=True
            ),
        ),
    )
    bins = data.draw(bins_strategy)

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
        result, bins_out = pd.cut(
            x,
            bins,
            right=right,
            labels=labels,
            retbins=retbins,
            precision=precision,
            include_lowest=include_lowest,
            duplicates=duplicates,
            ordered=ordered,
        )
    except ValueError:
        # Ignore cases where bins might be invalid (e.g., non-unique with duplicates='raise')
        return

    # Assertions based on API documentation:
    # 1. Output type:
    if labels is None:
        if isinstance(x, pd.Series):
            assert isinstance(result, pd.Series)
        else:
            assert isinstance(result, pd.Categorical)
    elif labels is False:
        assert isinstance(result, (np.ndarray, pd.Index))
    else:
        assert isinstance(result, (pd.Categorical, pd.Series))

    # 2. Bins are returned when retbins=True
    if retbins:
        if isinstance(bins, pd.IntervalIndex):
            assert bins is bins_out
        else:
            assert isinstance(bins_out, np.ndarray)

    # 3. Ordered property of Categorical output
    if isinstance(result, pd.Categorical):
        assert result.ordered is ordered

    # 4. NA values remain NA in the result
    assert pd.isna(result).all() == pd.isna(x).all()


# End program