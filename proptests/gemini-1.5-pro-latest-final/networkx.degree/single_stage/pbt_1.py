from hypothesis import given, strategies as st
import networkx as nx

# Summary: Generates diverse graphs, node bunches, and weight parameters.
@given(st.data())
def test_networkx_degree(data):
    # Generate graph types:
    graph_types = [nx.Graph, nx.DiGraph, nx.MultiGraph]
    graph_type = data.draw(st.sampled_from(graph_types))
    G = graph_type()

    # Generate nodes and edges:
    num_nodes = data.draw(st.integers(min_value=0, max_value=10))
    nodes = range(num_nodes)
    G.add_nodes_from(nodes)
    
    # Add edges with optional weights:
    for _ in range(data.draw(st.integers(min_value=0, max_value=20))):
        u, v = data.draw(st.tuples(st.sampled_from(nodes), st.sampled_from(nodes)))
        weight = data.draw(st.one_of(st.none(), st.integers(), st.floats()))
        G.add_edge(u, v, weight=weight)

    # Generate node bunch:
    nbunch_options = [None, data.draw(st.sampled_from(nodes)), data.draw(st.lists(st.sampled_from(nodes)))]
    nbunch = data.draw(st.sampled_from(nbunch_options))

    # Generate weight parameter:
    weight_param = data.draw(st.one_of(st.none(), st.just("weight")))

    # Check degree calculation and data type:
    degree_result = nx.degree(G, nbunch, weight=weight_param)
    if nbunch is None:
        assert isinstance(degree_result, dict)
        for node in G.nodes:
            assert degree_result[node] == len(G[node]) 
    else:
        assert isinstance(degree_result, nx.classes.reportviews.DegreeView) 
        # Add assertions for degree calculation based on nbunch and weight

# End program