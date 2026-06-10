from hypothesis import given, strategies as st
import networkx as nx

# Summary: Generate random graphs (Graph/DiGraph/MultiGraph) with integer nodes,
# random weighted edges, and randomly choose nbunch (None / single node / subset)
# and weight (None / "weight"). Check return types, value consistency, the
# handshaking lemma for undirected unweighted graphs, and non-negativity.
@given(st.data())
def test_networkx_degree(data):
    # Choose graph type
    graph_cls = data.draw(
        st.sampled_from([nx.Graph, nx.DiGraph, nx.MultiGraph]),
        label="graph_cls",
    )
    G = graph_cls()

    # Generate nodes
    nodes = data.draw(
        st.lists(st.integers(min_value=0, max_value=15), unique=True, max_size=10),
        label="nodes",
    )
    G.add_nodes_from(nodes)

    # Generate edges between existing nodes with random weights
    if nodes:
        edges = data.draw(
            st.lists(
                st.tuples(
                    st.sampled_from(nodes),
                    st.sampled_from(nodes),
                    st.floats(
                        min_value=0.0,
                        max_value=100.0,
                        allow_nan=False,
                        allow_infinity=False,
                    ),
                ),
                max_size=20,
            ),
            label="edges",
        )
        for u, v, w in edges:
            G.add_edge(u, v, weight=w)

    # Choose weight parameter
    weight = data.draw(st.sampled_from([None, "weight"]), label="weight")

    # Choose nbunch: None, a single node, or a subset
    all_nodes = list(G.nodes())
    nbunch_choice = data.draw(
        st.sampled_from(["none", "single", "subset"]), label="nbunch_choice"
    )

    if nbunch_choice == "single" and all_nodes:
        node = data.draw(st.sampled_from(all_nodes), label="single_node")
        result = nx.degree(G, node, weight=weight)
        # Property 1: single node -> integer/numeric degree
        assert isinstance(result, (int, float))
        # Property 4: non-negativity
        assert result >= 0
        # Property 5: consistency with direct access
        assert result == G.degree(node, weight=weight)
        return

    if nbunch_choice == "subset" and all_nodes:
        k = data.draw(
            st.integers(min_value=0, max_value=len(all_nodes)), label="subset_size"
        )
        nbunch = all_nodes[:k]
    else:
        nbunch = None

    result = nx.degree(G, nbunch, weight=weight)

    # Property 2: result is iterable yielding (node, degree) pairs over a subset
    covered_nodes = set()
    total_degree = 0
    for n, d in result:
        assert n in G  # nodes must belong to the graph
        # Property 4: non-negativity
        assert d >= 0
        # Property 5: consistency with direct access
        assert d == G.degree(n, weight=weight)
        covered_nodes.add(n)
        total_degree += d

    assert covered_nodes.issubset(set(G.nodes()))

    # Property 3: handshaking lemma for undirected, unweighted, full-node case
    if nbunch is None and weight is None and not G.is_directed():
        assert total_degree == 2 * G.number_of_edges()
# End program