from hypothesis import given, strategies as st
import numpy as np
import pandas as pd

# Summary: Generate 1-D list/ndarray/Series inputs with finite floats and NaNs; generate scalar, edge-sequence, and IntervalIndex bins, including duplicate edge handling with duplicates="drop"; vary right/include_lowest/precision/retbins/labels/ordered. Check documented properties: length and Series index preservation, NA propagation, retbins shape/value, label/code validity, categorical ordering, and exact in-bin vs out-of-bin NA behavior for explicit bins.
@given(st.data())
def test_pandas_cut(data):
    finite_float = st.floats(
        min_value=-1000,
        max_value=1000,
        allow_nan=False,
        allow_infinity=False,
        width=32,
    )

    x_values = data.draw(
        st.lists(
            st.one_of(finite_float, st.just(np.nan)),
            min_size=1,
            max_size=25,
        ).filter(lambda xs: any(not pd.isna(v) for v in xs))
    )

    container_kind = data.draw(st.sampled_from(["list", "ndarray", "series"]))
    if container_kind == "list":
        x = list(x_values)
        x_is_series = False
    elif container_kind == "ndarray":
        x = np.asarray(x_values, dtype=float)
        x_is_series = False
    else:
        index = data.draw(
            st.lists(st.integers(-50, 50), min_size=len(x_values), max_size=len(x_values))
        )
        x = pd.Series(x_values, index=index)
        x_is_series = True

    bins_kind = data.draw(st.sampled_from(["int", "sequence", "interval"]))
    right = data.draw(st.booleans())
    include_lowest = data.draw(st.booleans())
    precision = data.draw(st.integers(min_value=0, max_value=6))
    retbins = data.draw(st.booleans())

    effective_edges = None

    if bins_kind == "int":
        bins = data.draw(st.integers(min_value=1, max_value=8))
        n_intervals = bins
        duplicates = data.draw(st.sampled_from(["raise", "drop"]))

    elif bins_kind == "sequence":
        base_edges = data.draw(
            st.lists(finite_float, min_size=2, max_size=10)
            .filter(lambda xs: len(set(map(float, xs))) >= 2)
        )
        effective_edges = sorted(set(map(float, base_edges)))
        bins_list = list(effective_edges)

        if data.draw(st.booleans()):
            duplicate_position = data.draw(
                st.integers(min_value=0, max_value=len(bins_list) - 1)
            )
            bins_list.insert(duplicate_position, bins_list[duplicate_position])
            duplicates = "drop"
        else:
            duplicates = data.draw(st.sampled_from(["raise", "drop"]))

        bins = bins_list
        n_intervals = len(effective_edges) - 1

    else:
        raw_edges = data.draw(
            st.lists(finite_float, min_size=2, max_size=10)
            .filter(lambda xs: len(set(map(float, xs))) >= 2)
        )
        interval_edges = sorted(set(map(float, raw_edges)))

        if len(interval_edges) >= 4 and data.draw(st.booleans()):
            pairs = list(zip(interval_edges[::2], interval_edges[1::2]))
        else:
            pairs = [(interval_edges[0], interval_edges[-1])]

        closed = data.draw(st.sampled_from(["left", "right", "both", "neither"]))
        bins = pd.IntervalIndex.from_tuples(pairs, closed=closed)
        n_intervals = len(bins)
        duplicates = data.draw(st.sampled_from(["raise", "drop"]))

    if bins_kind == "interval":
        labels = None
        ordered = True
    else:
        label_kind = data.draw(st.sampled_from(["none", "false", "unique_labels", "duplicate_labels"]))

        if label_kind == "none":
            labels = None
            ordered = True
        elif label_kind == "false":
            labels = False
            ordered = True
        elif label_kind == "unique_labels":
            prefix = data.draw(st.text(min_size=0, max_size=3))
            labels = [f"{prefix}_label_{i}" for i in range(n_intervals)]
            ordered = data.draw(st.booleans())
        else:
            alphabet = ["A", "B", "C"]
            labels = data.draw(
                st.lists(
                    st.sampled_from(alphabet),
                    min_size=n_intervals,
                    max_size=n_intervals,
                )
            )
            ordered = False

    result = pd.cut(
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

    if retbins:
        out, returned_bins = result
    else:
        out = result
        returned_bins = None

    assert len(out) == len(x_values)

    if x_is_series:
        assert isinstance(out, pd.Series)
        assert out.index.equals(x.index)
    elif labels is False:
        assert isinstance(out, np.ndarray)
    else:
        assert isinstance(out, pd.Categorical)

    out_values = list(out)

    for original, binned in zip(x_values, out_values):
        if pd.isna(original):
            assert pd.isna(binned)

    if retbins:
        if bins_kind == "int":
            assert isinstance(returned_bins, np.ndarray)
            assert len(returned_bins) == bins + 1
            assert np.all(np.diff(returned_bins) > 0)
        elif bins_kind == "sequence":
            assert isinstance(returned_bins, np.ndarray)
            assert np.allclose(returned_bins, np.asarray(effective_edges), equal_nan=True)
        else:
            assert isinstance(returned_bins, pd.IntervalIndex)
            assert returned_bins.equals(bins)

    if labels is False:
        for value in out_values:
            if not pd.isna(value):
                assert float(value).is_integer()
                assert 0 <= int(value) < n_intervals

    if labels not in (None, False):
        label_set = set(labels)
        for value in out_values:
            if not pd.isna(value):
                assert value in label_set

    if labels is not False:
        if isinstance(out, pd.Series):
            assert str(out.dtype) == "category"
            assert out.cat.ordered == ordered
        else:
            assert isinstance(out, pd.Categorical)
            assert out.ordered == ordered

        if bins_kind == "interval":
            categories = out.cat.categories if isinstance(out, pd.Series) else out.categories
            assert categories.equals(bins)

    if bins_kind == "int":
        for original, binned in zip(x_values, out_values):
            if not pd.isna(original):
                assert not pd.isna(binned)

    elif bins_kind == "sequence":
        left_edge = effective_edges[0]
        right_edge = effective_edges[-1]

        for original, binned in zip(x_values, out_values):
            if pd.isna(original):
                continue

            if right:
                covered = (left_edge < original <= right_edge) or (
                    include_lowest and original == left_edge
                )
            else:
                covered = left_edge <= original < right_edge

            assert pd.isna(binned) != covered

    else:
        for original, binned in zip(x_values, out_values):
            if pd.isna(original):
                continue

            covered = any(original in interval for interval in bins)
            assert pd.isna(binned) != covered

# End program