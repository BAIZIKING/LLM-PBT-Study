from hypothesis import given, strategies as st
import itertools
import networkx as nx
import pytest

# Summary: Generate small undirected NetworkX graphs with varied hashable node labels,
# including empty graphs, sparse/random graphs, complete graphs, isolated nodes, and
# self-loops. Then generate the optional `nodes` argument as either None, a valid clique
# subset, or an invalid non-clique / missing-node case. Check that valid calls return
# exactly the brute-force maximal cliques, filtered by `nodes` when provided; check that
# invalid `nodes` raises ValueError.
@given(st.data())
def test_networkx_find_cliques(data):
    label_strategy = st.one_of(
        st.integers(min_value=-5, max_value=5),
        st.text(min_size=0, max_size=3),
        st.tuples(st.integers(min_value=0, max_value=3), st.text(max_size=2)),
    )

    n = data.draw(st.integers(min_value=0, max_value=8))
    labels = data.draw(
        st.lists(label_strategy, min_size=n, max_size=n, unique=True)
    )

    G = nx.Graph()
    G.add_nodes_from(labels)

    pairs = list(itertools.combinations(labels, 2))
    edge_mode = data.draw(st.sampled_from(["empty", "complete", "random"]))

    if edge_mode == "complete":
        G.add_edges_from(pairs)
    elif edge_mode == "random":
        for u, v in pairs:
            if data.draw(st.booleans()):
                G.add_edge(u, v)

    # Self-loops should be ignored by find_cliques, so include them as edge cases.
    for node in labels:
        if data.draw(st.booleans()):
            G.add_edge(node, node)

    def is_clique(nodes):
        return all(G.has_edge(u, v) for u, v in itertools.combinations(nodes, 2))

    def is_maximal_clique(nodes):
        node_set = set(nodes)
        return is_clique(nodes) and not any(
            outside not in node_set
            and all(G.has_edge(outside, inside) for inside in node_set)
            for outside in labels
        )

    all_clique_subsets = [[]]
    for r in range(1, len(labels) + 1):
        for subset in itertools.combinations(labels, r):
            if is_clique(subset):
                all_clique_subsets.append(list(subset))

    brute_force_maximal = [
        list(subset)
        for r in range(1, len(labels) + 1)
        for subset in itertools.combinations(labels, r)
        if is_maximal_clique(subset)
    ]

    nodes_case = data.draw(st.sampled_from(["none", "valid", "invalid"]))

    if nodes_case == "none":
        nodes_arg = None
        should_raise = False
    elif nodes_case == "valid":
        nodes_arg = data.draw(st.sampled_from(all_clique_subsets))
        should_raise = False
    else:
        non_edges = [(u, v) for u, v in pairs if not G.has_edge(u, v)]
        if non_edges and data.draw(st.booleans()):
            nodes_arg = list(data.draw(st.sampled_from(non_edges)))
        else:
            nodes_arg = [("__definitely_missing_node__",)]
        should_raise = True

    if should_raise:
        with pytest.raises(ValueError):
            list(nx.find_cliques(G, nodes=nodes_arg))
        return

    actual = list(nx.find_cliques(G, nodes=nodes_arg))

    required_nodes = set() if nodes_arg is None else set(nodes_arg)
    expected = [
        clique
        for clique in brute_force_maximal
        if required_nodes.issubset(set(clique))
    ]

    assert {frozenset(clique) for clique in actual} == {
        frozenset(clique) for clique in expected
    }

    for clique in actual:
        assert isinstance(clique, list)
        assert set(clique).issubset(set(labels))
        assert required_nodes.issubset(set(clique))
        assert is_clique(clique)
        assert is_maximal_clique(clique)
# End program