from hypothesis import given, strategies as st
import networkx as nx

@given(st.data())
def test_networkx_degree(data):
    # Generate a random graph G
    G = nx.gnp_random_graph(data.draw(st.integers(min_value=0, max_value=10)), 0.5)

    # Generate nbunch as a subset of nodes
    if G.number_of_nodes() > 0:
        nodes = list(G.nodes())
        nbunch = data.draw(st.lists(st.sampled_from(nodes), max_size=5))
    else:
        nbunch = None

    # Generate weight as string or None
    weight = data.draw(st.one_of(st.none(), st.text()))

    # Run the degree function
    degrees = nx.degree(G, nbunch, weight)

    # Check the properties
    for n, d in degrees:
        assert 0 <= d < G.number_of_nodes()
# End program