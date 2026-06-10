from hypothesis import given, strategies as st
import networkx as nx

# Summary: Generate random simple graphs with integer nodes, random edges
# (optionally weighted), then test degree() with nbunch=None, a single node,
# and a subset of nodes, against weight=None and weight="weight".
@given(st.data())
def test_networkx_degree(data):
    # Generate nodes (allow empty graph as edge case)
    nodes = data.draw(st.lists(st.integers(min_value=0, max_value=20),
                               min_size=0, max_size=10, unique=True))

    # Generate edges between existing nodes (allow self-loops)
    if nodes:
        edges = data.draw(st.lists(
            st.tuples(st.sampled_from(nodes), st.sampled_from(nodes)),
            min_size=0, max_size=20))
    else:
        edges = []

    # Decide whether to use weights
    use_weight = data.draw(st.booleans())

    G = nx.Graph()
    G.add_nodes_from(nodes)
    for (u, v) in edges:
        w = data.draw(st.floats(min_value=0, max_value=100,
                                allow_nan=False, allow_infinity=False))
        G.add_edge(u, v, weight=w)

    weight = "weight" if use_weight else None

    # --- Property 1: nbunch=None returns degrees for all nodes ---
    full_view = nx.degree(G, nbunch=None, weight=weight)
    full_dict = dict(full_view)
    assert set(full_dict.keys()) == set(G.nodes())

    # --- Property 5: all degrees are non-negative ---
    for d in full_dict.values():
        assert d >= 0

    # --- Property 4: handshake lemma for the unweighted case ---
    if weight is None:
        unweighted = dict(nx.degree(G))
        assert sum(unweighted.values()) == 2 * G.number_of_edges()

    if nodes:
        # --- Property 2: single node returns matching scalar degree ---
        single = data.draw(st.sampled_from(nodes))
        single_deg = nx.degree(G, nbunch=single, weight=weight)
        assert single_deg == full_dict[single]

        # --- Property 3: subset of nodes returns matching degrees ---
        subset = data.draw(st.lists(st.sampled_from(nodes),
                                    min_size=0, max_size=len(nodes),
                                    unique=True))
        subset_view = nx.degree(G, nbunch=subset, weight=weight)
        subset_dict = dict(subset_view)
        assert set(subset_dict.keys()) == set(subset)
        for n in subset:
            assert subset_dict[n] == full_dict[n]
# End program