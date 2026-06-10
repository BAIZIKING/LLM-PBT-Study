from hypothesis import given, strategies as st
import pandas as pd


# Summary: This strategy generates diverse inputs for pandas.cut, including:
# - x: array-like data (lists of floats)
# - bins: different binning criteria (int for number of bins, list of floats for bin edges, IntervalIndex)
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
    bins_strategy = st.one_of(
        st.integers(min_value=1),
        st.lists(st.floats(), min_size=2, unique=True),
        st.builds(pd.IntervalIndex.from_tuples, st.lists(st.tuples(st.floats(), st.floats()))),
    )
    bins = data.draw(bins_strategy)
    right = data.draw(st.booleans())
    labels = data.draw(st.one_of(st.none(), st.lists(st.text())))
    retbins = data.draw(st.booleans())
    precision = data.draw(st.integers(min_value=0))
    include_lowest = data.draw(st.booleans())
    duplicates = data.draw(st.sampled_from(["raise", "drop"]))
    ordered = data.draw(st.booleans())

    # Check that the function doesn't raise unexpected errors
    try:
        result, bins_out = pd.cut(x, bins, right=right, labels=labels, retbins=retbins, precision=precision,
                                  include_lowest=include_lowest, duplicates=duplicates, ordered=ordered)
    except ValueError as e:
        # ValueError is expected when bins are not unique and duplicates='raise'
        if duplicates == "raise" and not isinstance(bins, pd.IntervalIndex):
            assert "Bin edges must be unique" in str(e)
        else:
            raise

    # Check properties based on the API documentation:
    if isinstance(result, pd.Categorical):
        # Check that the categories are correct
        expected_categories = pd.IntervalIndex.from_tuples([(b, bins[i + 1]) for i, b in enumerate(bins[:-1])],
                                                           closed="right" if right else "left")
        if include_lowest:
            expected_categories = pd.IntervalIndex.from_tuples([(bins[0], bins[1])] + expected_categories.tolist(),
                                                               closed="right" if right else "left")
        assert result.categories.equals(expected_categories)

        # Check that the order of categories is correct
        assert result.ordered == ordered

    # Check that the returned bins are correct
    if retbins:
        if isinstance(bins, pd.IntervalIndex):
            assert bins_out.equals(bins)
        else:
            expected_bins = pd.unique(bins) if duplicates == "drop" else bins
            assert (bins_out == expected_bins).all()

# End program