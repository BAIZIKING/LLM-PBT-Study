from hypothesis import given, strategies as st
import networkx


@st.composite
def graphs(draw, weighted=False, allow_selfloops=True):
    nodes = draw(st.lists(st.integers(min_value=0, max_value=30), max_size=20, unique=True))
    if not nodes:
        nodes = [0]
    node_sampler = st.sampled_from(nodes)
    if allow_selfloops:
        edge_strategy = st.tuples(node_sampler, node_sampler)
    else:
        edge_strategy = st.tuples(node_sampler, node_sampler).filter(lambda e: e[0] != e[1])
    edges = draw(st.lists(edge_strategy, max_size=40))
    G = networkx.Graph()
    G.add_nodes_from(nodes)
    for u, v in edges:
        if weighted:
            w = draw(st.integers(min_value=0, max_value=1000))
            G.add_edge(u, v, weight=w)
        else:
            G.add_edge(u, v)
    return G


@given(st.data())
def test_networkx_degree_property(data):
    # Property 1: Non-negativity and integer type (unweighted).
    G1 = data.draw(graphs(weighted=False))
    for node, d in networkx.degree(G1):
        assert isinstance(d, int)
        assert d >= 0

    # Property 2: Handshaking lemma.
    G2 = data.draw(graphs(weighted=False))
    total = sum(d for _, d in networkx.degree(G2))
    assert total == 2 * G2.number_of_edges()

    # Property 3: Consistency with node count.
    G3 = data.draw(graphs(weighted=False))
    deg_nodes = set(n for n, _ in networkx.degree(G3))
    assert deg_nodes == set(G3.nodes())
    assert len(list(networkx.degree(G3))) == G3.number_of_nodes()

    # Property 4: Single node consistency.
    G4 = data.draw(graphs(weighted=False))
    full = dict(networkx.degree(G4))
    for n in G4.nodes():
        single = networkx.degree(G4, n)
        assert single == full[n]
        incident = sum(2 if u == v else 1 for u, v in G4.edges(n))
        assert single == incident

    # Property 5: Weighted degree equals sum of incident weights.
    G5 = data.draw(graphs(weighted=True))
    wview = dict(networkx.degree(G5, weight="weight"))
    for n in G5.nodes():
        expected = sum((2 * w if u == v else w)
                       for u, v, w in G5.edges(n, data="weight"))
        assert wview[n] == expected

    H = networkx.Graph()
    H.add_nodes_from(G5.nodes())
    for u, v in G5.edges():
        H.add_edge(u, v, weight=1)
    uw = dict(networkx.degree(H))
    w1 = dict(networkx.degree(H, weight="weight"))
    for n in H.nodes():
        assert uw[n] == w1[n]
# End program