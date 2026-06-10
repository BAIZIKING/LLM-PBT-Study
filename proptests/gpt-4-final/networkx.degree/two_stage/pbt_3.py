from hypothesis import given, strategies as st
import networkx as nx 
import random

@given(st.data())
def test_degree_property(data):
    n = data.draw(st.integers(min_value=0, max_value=500))
    G = nx.gnm_random_graph(n, random.randint(n-1, n*(n-1)//2))

    degree_view = G.degree()

    # Type Check
    assert type(degree_view) == nx.classes.reportviews.DegreeView

    # Content Check
    for node, degree in degree_view:
        assert type(node) == int
        assert type(degree) == int
        assert degree >= 0

    # Size Check
    assert len(degree_view) == len(G.nodes())

    # Node Existence
    nbunch = data.draw(st.sampled_from(list(G.nodes())), elements=st.integers(min_value=0, max_value=len(G.nodes())-1))
    degree_view_nbunch = G.degree(nbunch)
    assert len(degree_view_nbunch) == len(nbunch)

    # Weight Influence
    G = nx.gnm_random_graph(n, random.randint(n-1, n*(n-1)//2), seed=42)
    for (u, v) in G.edges():
        G[u][v]['weight'] = random.randint(1, 10)
    weighted_degree_view = G.degree(weight='weight')
    for node, weighted_degree in weighted_degree_view:
        assert weighted_degree >= degree_view[node]
# End program