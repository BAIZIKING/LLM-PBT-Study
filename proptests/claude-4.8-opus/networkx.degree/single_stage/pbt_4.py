from hypothesis import given, strategies as st
import networkx as nx

# Summary: Generate random graphs (nodes + weighted edges) including empty/single-node
# edge cases, then choose nbunch as None, a single existing node, or a subset of nodes,
# and weight as None or "weight". Verify the degree view's structure, single-node return
# type, subset membership, value consistency across calls, and the handshaking lemma.
@given(st.data())
def test_networkx_degree(data):
    # Build a set of nodes (allow empty graph as edge case)
    nodes = data.draw(st.lists(st.integers(min_value=0, max_value=10), unique=True, max_size=8))
    G = nx.Graph()
    G.add_nodes_from(nodes)

    # Add random edges (only if we have nodes) with random weights
    if nodes:
        num_edges = data.draw(st.integers(min_value=0, max_value=15))
        for _ in range(num_edges):
            u = data.draw(st.sampled_from(nodes))
            v = data.draw(st.sampled_from(nodes))
            w = data.draw(st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False))
            G.add_edge(u, v, weight=w)

    # Choose weight parameter
    weight = data.draw(st.sampled_from([None, "weight"]))

    # Reference: degree view over all nodes
    all_deg = dict(nx.degree(G, nbunch=None, weight=weight))

    # Property 1: all-nodes view contains exactly all graph nodes, non-negative degrees
    assert set(all_deg.keys()) == set(G.nodes())
    for node, d in all_deg.items():
        assert d >= 0

    # Property 4: handshaking lemma (unweighted only, exact integer relation)
    if weight is None:
        assert sum(all_deg.values()) == 2 * G.number_of_edges()

    # Choose nbunch: None, a single existing node, or a subset of existing nodes
    if not G.nodes():
        nbunch_choice = data.draw(st.sampled_from(["none"]))
    else:
        nbunch_choice = data.draw(st.sampled_from(["none", "single", "subset"]))

    if nbunch_choice == "none":
        result = nx.degree(G, nbunch=None, weight=weight)
        assert dict(result) == all_deg

    elif nbunch_choice == "single":
        node = data.draw(st.sampled_from(list(G.nodes())))
        # Property 2: single existing node returns a single integer degree value
        single_deg = nx.degree(G, nbunch=node, weight=weight)
        assert single_deg == all_deg[node]

    else:  # subset
        subset = data.draw(st.lists(st.sampled_from(list(G.nodes())), unique=True))
        sub_deg = dict(nx.degree(G, nbunch=subset, weight=weight))
        # Property 3: subset view nodes are a subset of all nodes with matching values
        assert set(sub_deg.keys()).issubset(set(G.nodes()))
        for node, d in sub_deg.items():
            assert d == all_deg[node]
# End program