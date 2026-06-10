from hypothesis import given, strategies as st
import networkx

@given(st.data())
def test_networkx_find_cliques_property(data):
    n = data.draw(st.integers(min_value=0, max_value=8))

    G = networkx.Graph()
    G.add_nodes_from(range(n))

    possible_edges = [(u, v) for u in range(n) for v in range(u, n)]
    edges = data.draw(
        st.lists(
            st.sampled_from(possible_edges),
            unique=True,
            max_size=len(possible_edges),
        )
        if possible_edges
        else st.just([])
    )
    G.add_edges_from(edges)

    use_nodes_argument = data.draw(st.booleans())

    if use_nodes_argument:
        nodes = data.draw(
            st.lists(
                st.integers(min_value=0, max_value=n - 1),
                unique=True,
                max_size=n,
            )
            if n > 0
            else st.just([])
        )
    else:
        nodes = None

    def is_complete(node_list):
        return all(
            G.has_edge(u, v)
            for i, u in enumerate(node_list)
            for v in node_list[i + 1 :]
        )

    if nodes is not None and not is_complete(nodes):
        try:
            list(networkx.find_cliques(G, nodes=nodes))
        except ValueError:
            return
        assert False, "find_cliques should raise ValueError when nodes is not a clique"

    if nodes is None:
        cliques = list(networkx.find_cliques(G))
    else:
        cliques = list(networkx.find_cliques(G, nodes=nodes))

    seen_cliques = set()

    for clique in cliques:
        assert isinstance(clique, list)
        assert len(clique) == len(set(clique))
        assert all(node in G for node in clique)

        assert is_complete(clique)

        clique_set = set(clique)
        for outside_node in set(G.nodes) - clique_set:
            assert not all(G.has_edge(outside_node, node) for node in clique_set)

        frozen_clique = frozenset(clique)
        assert frozen_clique not in seen_cliques
        seen_cliques.add(frozen_clique)

        if nodes is not None:
            assert set(nodes).issubset(clique_set)

# End program