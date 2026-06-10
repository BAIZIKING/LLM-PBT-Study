from hypothesis import given, strategies as st
import itertools
import pytest
import networkx as nx

# Summary: Generate small undirected Graph/MultiGraph inputs with arbitrary, empty,
# complete, path, and star structures, including self-loops and parallel edges.
# Also generate optional `nodes` filters from existing graph nodes; these may or
# may not form a clique. Check that results are exactly the brute-force maximal
# cliques, that every returned clique is complete and maximal, that `nodes` is
# respected, and that non-clique `nodes` raises ValueError.
@given(st.data())
def test_networkx_find_cliques(data):
    n = data.draw(st.integers(min_value=0, max_value=8), label="n")
    graph_type = data.draw(st.sampled_from(["graph", "multigraph"]), label="graph_type")
    shape = data.draw(
        st.sampled_from(["arbitrary", "empty", "complete", "path", "star"]),
        label="shape",
    )

    G = nx.MultiGraph() if graph_type == "multigraph" else nx.Graph()
    graph_nodes = list(range(n))
    G.add_nodes_from(graph_nodes)

    all_edges = list(itertools.combinations(graph_nodes, 2))

    if shape == "empty":
        chosen_edges = []
    elif shape == "complete":
        chosen_edges = all_edges
    elif shape == "path":
        chosen_edges = [(i, i + 1) for i in range(max(0, n - 1))]
    elif shape == "star":
        chosen_edges = [(0, i) for i in range(1, n)] if n else []
    else:
        chosen_edges = (
            list(
                data.draw(
                    st.sets(
                        st.sampled_from(all_edges),
                        min_size=0,
                        max_size=len(all_edges),
                    ),
                    label="chosen_edges",
                )
            )
            if all_edges
            else []
        )

    for u, v in chosen_edges:
        if graph_type == "multigraph":
            multiplicity = data.draw(st.integers(min_value=1, max_value=3), label="edge_multiplicity")
            for _ in range(multiplicity):
                G.add_edge(u, v)
        else:
            G.add_edge(u, v)

    loop_nodes = (
        data.draw(
            st.sets(st.sampled_from(graph_nodes), min_size=0, max_size=n),
            label="loop_nodes",
        )
        if graph_nodes
        else set()
    )
    for u in loop_nodes:
        if graph_type == "multigraph":
            multiplicity = data.draw(st.integers(min_value=1, max_value=3), label="loop_multiplicity")
            for _ in range(multiplicity):
                G.add_edge(u, u)
        else:
            G.add_edge(u, u)

    nodes_mode = data.draw(st.sampled_from(["none", "list"]), label="nodes_mode")
    if nodes_mode == "none":
        nodes_arg = None
    elif graph_nodes:
        nodes_arg = data.draw(
            st.lists(
                st.sampled_from(graph_nodes),
                min_size=0,
                max_size=n,
                unique=True,
            ),
            label="nodes_arg",
        )
    else:
        nodes_arg = []

    def is_clique(nodes):
        return all(
            G.has_edge(u, v)
            for u, v in itertools.combinations(nodes, 2)
        )

    def is_maximal_clique(nodes):
        node_set = set(nodes)
        if not node_set or not is_clique(node_set):
            return False
        return not any(
            all(G.has_edge(candidate, member) for member in node_set)
            for candidate in set(G.nodes) - node_set
        )

    def brute_force_maximal_cliques():
        maximal = set()
        for r in range(1, n + 1):
            for subset in itertools.combinations(graph_nodes, r):
                subset_set = frozenset(subset)
                if is_maximal_clique(subset_set):
                    maximal.add(subset_set)
        return maximal

    if nodes_arg is not None and not is_clique(nodes_arg):
        with pytest.raises(ValueError):
            list(nx.find_cliques(G, nodes=nodes_arg))
        return

    actual_cliques = list(nx.find_cliques(G, nodes=nodes_arg))
    actual = {frozenset(clique) for clique in actual_cliques}

    expected = brute_force_maximal_cliques()
    if nodes_arg is not None:
        required = set(nodes_arg)
        expected = {
            clique
            for clique in expected
            if required <= clique
        }

    assert actual == expected

    for clique in actual_cliques:
        assert len(clique) == len(set(clique))
        assert set(clique) <= set(G.nodes)
        assert is_clique(clique)
        assert is_maximal_clique(clique)
        if nodes_arg is not None:
            assert set(nodes_arg) <= set(clique)
# End program