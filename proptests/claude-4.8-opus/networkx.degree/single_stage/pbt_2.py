from hypothesis import given, strategies as st
import networkx as nx

# Summary: Build a random graph from generated nodes and weighted edges, then
# randomly select nbunch (None / single node / subset) and weight (None / "weight").
# Verify return-type behavior, the handshaking lemma, non-negativity, and
# consistency between full-graph and per-node queries.
@given(st.data())
def test_networkx_degree(data):
    # Generate nodes
    nodes = data.draw(st.lists(st.integers(min_value=0, max_value=20),
                               min_size=0, max_size=10, unique=True))

    # Generate weighted edges only between existing nodes
    if nodes:
        edges = data.draw(st.lists(
            st.tuples(st.sampled_from(nodes),
                      st.sampled_from(nodes),
                      st.floats(min_value=0.1, max_value=100,
                                allow_nan=False, allow_infinity=False)),
            min_size=0, max_size=15))
    else:
        edges = []

    G = nx.Graph()
    G.add_nodes_from(nodes)
    for u, v, w in edges:
        G.add_edge(u, v, weight=w)

    # Choose weight parameter
    weight = data.draw(st.sampled_from([None, "weight"]))

    # Choose nbunch: None, a single node, or a subset of nodes
    graph_nodes = list(G.nodes())
    if graph_nodes:
        nbunch_kind = data.draw(st.sampled_from(["none", "single", "subset"]))
        if nbunch_kind == "none":
            nbunch = None
        elif nbunch_kind == "single":
            nbunch = data.draw(st.sampled_from(graph_nodes))
        else:
            nbunch = data.draw(st.lists(st.sampled_from(graph_nodes),
                                        min_size=0, max_size=len(graph_nodes),
                                        unique=True))
    else:
        nbunch = None

    result = nx.degree(G, nbunch=nbunch, weight=weight)

    # Case 1: single node -> returns a scalar degree directly
    if graph_nodes and not isinstance(nbunch, (list, type(None))):
        deg = result
        assert isinstance(deg, (int, float))
        assert deg >= 0
        # Consistency with full-graph query
        full = dict(nx.degree(G, weight=weight))
        assert deg == full[nbunch]
    else:
        # Case 2: None or subset -> iterable of (node, degree) pairs
        deg_dict = dict(result)
        # All degrees non-negative
        for node, d in deg_dict.items():
            assert d >= 0
            assert node in G.nodes()

        if nbunch is None:
            # Covers exactly all nodes
            assert set(deg_dict.keys()) == set(G.nodes())
            # Handshaking lemma (only meaningful for unweighted degree)
            if weight is None:
                assert sum(deg_dict.values()) == 2 * G.number_of_edges()
        else:
            # Subset: keys are a subset of requested nodes
            assert set(deg_dict.keys()).issubset(set(nbunch))
            # Consistency with full-graph query
            full = dict(nx.degree(G, weight=weight))
            for node, d in deg_dict.items():
                assert d == full[node]
# End program