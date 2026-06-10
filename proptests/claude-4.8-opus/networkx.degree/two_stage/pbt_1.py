from hypothesis import given, strategies as st, assume
import networkx


@st.composite
def graphs(draw, with_weights=False):
    n_nodes = draw(st.integers(min_value=0, max_value=20))
    nodes = list(range(n_nodes))
    G = networkx.Graph()
    G.add_nodes_from(nodes)
    if n_nodes >= 2:
        possible_edges = [(i, j) for i in nodes for j in nodes if i < j]
        edges = draw(
            st.lists(
                st.sampled_from(possible_edges),
                max_size=len(possible_edges),
                unique=True,
            )
        )
        if with_weights:
            for (u, v) in edges:
                w = draw(st.integers(min_value=0, max_value=1000))
                G.add_edge(u, v, weight=w)
        else:
            G.add_edges_from(edges)
    return G


@given(st.data())
def test_networkx_degree_property(data):
    # ---- Property 1: Sum of all degrees == 2 * number of edges (unweighted) ----
    G1 = data.draw(graphs())
    total_degree = sum(d for _, d in networkx.degree(G1))
    assert total_degree == 2 * G1.number_of_edges()

    # ---- Property 2: Degree values are non-negative ----
    G2 = data.draw(graphs(with_weights=True))
    for _, d in networkx.degree(G2):
        assert d >= 0
    for _, d in networkx.degree(G2, weight="weight"):
        assert d >= 0

    # ---- Property 3: Consistency with node set / nbunch ----
    G3 = data.draw(graphs())
    all_view_nodes = set(n for n, _ in networkx.degree(G3))
    assert all_view_nodes == set(G3.nodes())
    assert len(list(networkx.degree(G3))) == G3.number_of_nodes()
    if G3.number_of_nodes() > 0:
        nodes = list(G3.nodes())
        subset = data.draw(
            st.lists(st.sampled_from(nodes), unique=True, max_size=len(nodes))
        )
        view_subset_nodes = set(n for n, _ in networkx.degree(G3, nbunch=subset))
        assert view_subset_nodes == set(subset)

    # ---- Property 4: Single node returns scalar matching the full view ----
    G4 = data.draw(graphs())
    if G4.number_of_nodes() > 0:
        node = data.draw(st.sampled_from(list(G4.nodes())))
        full_view = networkx.degree(G4)
        single = networkx.degree(G4, nbunch=node)
        assert single == full_view[node]

    # ---- Property 5: Weighted degree relationships ----
    G5 = data.draw(graphs(with_weights=True))
    if G5.number_of_nodes() > 0:
        node = data.draw(st.sampled_from(list(G5.nodes())))
        weighted_deg = networkx.degree(G5, nbunch=node, weight="weight")
        expected_weighted = sum(
            G5[node][nbr].get("weight", 1) for nbr in G5.neighbors(node)
        )
        assert weighted_deg == expected_weighted

    # If all weights are 1, weighted degree == unweighted degree
    G6 = data.draw(graphs())
    for u, v in G6.edges():
        G6[u][v]["weight"] = 1
    for n in G6.nodes():
        assert networkx.degree(G6, nbunch=n, weight="weight") == networkx.degree(
            G6, nbunch=n
        )
# End program