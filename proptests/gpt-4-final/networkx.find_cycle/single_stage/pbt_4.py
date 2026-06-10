from hypothesis import given, strategies as st
import networkx as nx

@given(st.data())
def test_find_cycle(data):
    # Generate a list of nodes and edges.
    nodes = data.draw(st.lists(st.integers(min_value=0, max_value=20), min_size=0, max_size=10, unique=True))
    edges = data.draw(st.lists(st.tuples(st.sampled_from(nodes), st.sampled_from(nodes)), min_size=0, max_size=20, unique=True))
    
    # Create a directed or undirected graph.
    create_directed = data.draw(st.booleans())
    if create_directed:
        graph = nx.DiGraph()
    else:
        graph = nx.Graph()
    graph.add_nodes_from(nodes)
    graph.add_edges_from(edges)

    # Pick a random source node.
    source = data.draw(st.one_of(st.sampled_from(nodes), st.just(None)))
    
    # Set the orientation.
    orientation = data.draw(st.sampled_from(["original", "ignore", "reverse", None]))

    # Run the test
    try:
        cycle = nx.find_cycle(graph, source=source, orientation=orientation)
        assert all(e in edges for e in cycle)      
    except nx.NetworkXNoCycle:
        assert nx.is_directed_acyclic_graph(graph) or nx.is_tree(graph)