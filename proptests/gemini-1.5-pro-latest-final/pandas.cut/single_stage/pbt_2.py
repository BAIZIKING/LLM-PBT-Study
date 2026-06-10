from hypothesis import given, strategies as st
import pandas as pd


# Summary: This strategy generates diverse inputs for pandas.cut, including:
# - x: array-like data (lists of floats)
# - bins: different binning criteria (int for number of bins, lists of floats for custom bins, IntervalIndex)
# - right: True or False
# - labels: optional list of labels
# - retbins: True or False
# - precision: integer precision for bin labels
# - include_lowest: True or False
# - duplicates: 'raise' or 'drop'
# - ordered: True or False
@given(st.data())
def test_pandas_cut(data):
    x = data.draw(st.lists(st.floats()))
    bins = data.draw(
        st.one_of(
            st.integers(min_value=1),
            st.lists(st.floats(allow_nan=False), min_size=2),
            st.builds(pd.IntervalIndex.from_tuples, st.lists(st.tuples(st.floats(), st.floats()))),
        )
    )
    right = data.draw(st.booleans())
    labels = data.draw(st.one_of(st.none(), st.lists(st.text())))
    retbins = data.draw(st.booleans())
    precision = data.draw(st.integers(min_value=0))
    include_lowest = data.draw(st.booleans())
    duplicates = data.draw(st.sampled_from(["raise", "drop"]))
    ordered = data.draw(st.booleans())

    # Check that the function doesn't raise unexpected errors
    try:
        result, bins = pd.cut(
            x, bins, right=right, labels=labels, retbins=retbins, precision=precision, include_lowest=include_lowest, duplicates=duplicates, ordered=ordered
        )
    except ValueError as e:
        # Only allow ValueError for specific cases like non-overlapping bins
        assert "bins must be non-overlapping" in str(e)
        return

    # Check properties based on the API documentation:
    # 1. The length of the result should be equal to the length of x
    assert len(result) == len(x)

    # 2. If retbins is True, bins should be returned
    assert (retbins and bins is not None) or (not retbins and bins is None)

    # 3. If labels are provided, they should be reflected in the result
    if labels is not None:
        assert all(cat in labels for cat in result.categories)

    # 4. The order of the categories should match the 'ordered' parameter
    if labels is not None:
        assert result.ordered == ordered

    # 5. Check for NaN values in the result
    for i, value in enumerate(x):
        if pd.isna(value):
            assert pd.isna(result[i])

# End program