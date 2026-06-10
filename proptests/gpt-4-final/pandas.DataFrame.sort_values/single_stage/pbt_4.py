from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

@given(
    df=st.data().map(lambda data: pd.DataFrame({
        'col1': data.draw(st.lists(st.floats(allow_nan=True), min_size=1, max_size=10)),
        'col2': data.draw(st.lists(st.text(), min_size=1, max_size=10))
    })),
    by=st.lists(st.text(), min_size=1, max_size=2),
    ascending=st.booleans(),
    inplace=st.booleans(),
    kind=st.sampled_from(['quicksort', 'mergesort', 'heapsort', 'stable']),
    na_position=st.sampled_from(['first', 'last']),
    ignore_index=st.booleans()
)
def test_pandas_DataFrame_sort_values(df, by, ascending, inplace, kind, na_position, ignore_index):
    org_df= df.copy() # clone to test inplace result
    try:
        result = df.sort_values(by=by, ascending=ascending, inplace=inplace, kind=kind, na_position=na_position, ignore_index=ignore_index)
    except Exception as e:
        pass # to handle the KeyError due to non existing columns in by
    else:
        if inplace:
            np.testing.assert_array_equal(df.values, org_df.values)
        
        if ignore_index:
            np.testing.assert_array_equal(result.index, np.arange(len(df)))

        # when sorted the DataFrame, it should still have same length
        assert len(df) == len(result)
        
        # when sorted the DataFrame, the resulting DataFrame should be sorted
        if len(df) > 0:
            assert result[by].is_monotonic