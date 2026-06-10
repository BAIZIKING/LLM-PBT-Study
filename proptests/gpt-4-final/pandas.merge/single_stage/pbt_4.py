from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

@given(df1=st.dataframes(dtype=np.int64, columns=st.text(), index=st.range_indexes()), 
         df2=st.dataframes(dtype=np.int64, columns=st.text(), index=st.range_indexes()),
         how=st.sampled_from(['left', 'right', 'outer', 'inner', 'cross']),
         on=st.text(),
         left_on=st.text(),
         right_on=st.text(),
         left_index=st.booleans(),
         right_index=st.booleans(),
         sort=st.booleans(),
         suffixes=st.lists(st.text(), min_size=2, max_size=2))
def test_pandas_merge(df1, df2, how, on, left_on, right_on, left_index, right_index, sort, suffixes):
    if on in df1.columns and on in df2.columns : 
        merged_df = pd.merge(df1, df2, how=how, on=on, left_index=left_index, right_index=right_index, sort=sort, suffixes=suffixes) 

        # Property: The amount of data should not decrease, we only join data.
        assert(len(merged_df)>=min(len(df1),len(df2)))

        # Property: All column names in the resulting dataframe should come from the left or right dataframe or be the "on" column
        assert(all((name in df1.columns) or (name in df2.columns) or (name == on) for name in merged_df.columns))

        # Property: If we're doing a left join, all elements in the "on" column should be present in the original dataframe
        if how == 'left':
            assert(all(elem in df1[on].values for elem in merged_df[on].values))

        # Property: If we're doing a right join, all elements in the "on" column should be present in the original dataframe
        if how == 'right':
            assert(all(elem in df2[on].values for elem in merged_df[on].values))

        # Property: If we're doing an inner join, all elements in the "on" column should be present in both original dataframes
        if how == 'inner':
            assert(all((elem in df1[on].values) and (elem in df2[on].values) for elem in merged_df[on].values))

        # Property: If we're doing an outer join, all elements in the "on" column should be present in at least one of the original dataframes
        if how == 'outer':
            assert(all((elem in df1[on].values) or (elem in df2[on].values) for elem in merged_df[on].values))
# End program