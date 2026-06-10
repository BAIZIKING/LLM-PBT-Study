from hypothesis import given, strategies as st
import networkx as nx

# Summary: Generate small undirected graphs with heterogeneous hashable nodes, optional
# self-loops, sparse/dense edge sets, and integer edge weights that may be missing,
# zero, negative, or positive. Generate weight as None, an existing weight key, or a
# missing weight key. Generate nbunch as None, a single existing node, or a list/tuple
# of existing nodes plus non-graph nodes. Check that degree returns either the scalar
# degree for one node or a view whose pairs match an independent degree calculation:
# incident edges count once, self-loops count twice, and weighted degree uses edge
# attribute weight with default 1 when absent.
@given(st.data())
def test_networkx_degree(data):
    nodes = data.draw(
        st.lists(
            st.one_of(st.integers(-3, 3), st.text(min_size=0, max_size=3)),
            unique=True,
            max_size=8,
        )
    )

    G = nx.Graph()
    G.add_nodes_from(nodes)

    possible_edges = [
        (nodes[i], nodes[j])
        for i in range(len(nodes))
        for j in range(i, len(nodes))
    ]

    if possible_edges:
        edges = data.draw(
            st.lists(
                st.sampled_from(possible_edges),
                unique=True,
                max_size=len(possible_edges),
            )
        )
    else:
        edges = []

    for u, v in edges:
        if data.draw(st.booleans()):
            G.add_edge(u, v, w=data.draw(st.integers(-10, 10)))
        else:
            G.add_edge(u, v)

    weight = data.draw(st.one_of(st.none(), st.sampled_from(["w", "missing_key"])))

    if nodes:
        nbunch_kind = data.draw(st.sampled_from(["none", "single", "list", "tuple"]))
    else:
        nbunch_kind = data.draw(st.sampled_from(["none", "list", "tuple"]))

    if nbunch_kind == "none":
        nbunch = None
    elif nbunch_kind == "single":
        nbunch = data.draw(st.sampled_from(nodes))
    else:
        seq = data.draw(
            st.lists(
                st.one_of(
                    st.sampled_from(nodes) if nodes else st.nothing(),
                    st.integers(100, 110),
                ),
                max_size=12,
            )
        )
        nbunch = seq if nbunch_kind == "list" else tuple(seq)

    def expected_degree(node):
        total = 0
        for u, v, attrs in G.edges(data=True):
            edge_weight = 1 if weight is None else attrs.get(weight, 1)
            if u == node and v == node:
                total += 2 * edge_weight
            elif u == node or v == node:
                total += edge_weight
        return total

    result = nx.degree(G, nbunch=nbunch, weight=weight)

    if nbunch_kind == "single":
        assert result == expected_degree(nbunch)
    else:
        expected_nodes = nodes if nbunch is None else [n for n in nbunch if n in G]
        assert list(result) == [(n, expected_degree(n)) for n in expected_nodes]

# End program