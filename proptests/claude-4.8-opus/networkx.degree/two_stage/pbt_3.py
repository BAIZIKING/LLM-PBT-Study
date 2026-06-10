from hypothesis import given, strategies as st, assume
import networkx as nx


# Strategy to build a graph with optional edge weights
@st.composite
def graphs(draw, weighted=False):
    n_nodes = draw(st.integers(min_value=0, max_value=20))
    nodes = list(range(n_nodes))
    G = nx.Graph()
    G.add_nodes_from(nodes)
    if n_nodes >= 1:
        possible_edges = [(u, v) for u in nodes for v in nodes if u <= v]
        edges = draw(st.lists(st.sampled_from(possible_edges),
                              max_size=40, unique=True)) if possible_edges else []
        for (u, v) in edges:
            if weighted:
                w = draw(st.integers(min_value=0, max_value=1000))
                G.add_edge(u, v, weight=w)
            else:
                G.add_edge(u, v)
    return G


@given(st.data())
def test_networkx_degree_full_node_coverage():
    """Property 1: degree view (no nbunch) has exactly one entry per node."""
    import hypothesis
    @given(graphs())
    def inner(G):
        deg = nx.degree(G)
        deg_nodes = set(n for n, d in deg)
        assert deg_nodes == set(G.nodes())
        assert len(list(deg)) == G.number_of_nodes()
    inner()
# End program


@given(st.data())
def test_networkx_degree_handshaking_lemma():
    """Property 2: sum of degrees equals twice the number of edges."""
    @given(graphs())
    def inner(G):
        total_degree = sum(d for n, d in nx.degree(G))
        # self-loops count twice in networkx degree, handshaking still holds
        # since number_of_edges counts a self-loop once but degree counts it twice
        self_loops = nx.number_of_selfloops(G)
        expected = 2 * G.number_of_edges()
        assert total_degree == expected
    inner()
# End program


@given(st.data())
def test_networkx_degree_nonnegative_and_type():
    """Property 3: degrees are non-negative; integers when unweighted,
    equal sum of incident weights when weighted."""
    @given(st.booleans())
    def outer(weighted):
        @given(graphs(weighted=weighted))
        def inner(G):
            if weighted:
                deg = nx.degree(G, weight="weight")
                for n, d in deg:
                    assert d >= 0
                    expected = 0
                    for nbr, data in G[n].items():
                        w = data.get("weight", 1)
                        if nbr == n:
                            expected += 2 * w
                        else:
                            expected += w
                    assert d == expected
            else:
                deg = nx.degree(G)
                for n, d in deg:
                    assert isinstance(d, int)
                    assert d >= 0
        inner()
    outer()
# End program


@given(st.data())
def test_networkx_degree_single_node_consistency():
    """Property 4: single-node nbunch returns a scalar matching the full view."""
    @given(graphs())
    def inner(G):
        full = dict(nx.degree(G))
        for node in G.nodes():
            single = nx.degree(G, node)
            assert single == full[node]
            assert isinstance(single, int)
    inner()
# End program


@given(st.data())
def test_networkx_degree_subset_consistency():
    """Property 5: subset nbunch degrees match the full degree view."""
    @given(graphs(), st.data())
    def inner(G, data):
        nodes = list(G.nodes())
        full = dict(nx.degree(G))
        if nodes:
            subset = data.draw(st.lists(st.sampled_from(nodes),
                                        max_size=len(nodes), unique=True))
        else:
            subset = []
        subset_deg = dict(nx.degree(G, subset))
        assert set(subset_deg.keys()) == set(subset)
        for n in subset:
            assert subset_deg[n] == full[n]
    inner()
# End program