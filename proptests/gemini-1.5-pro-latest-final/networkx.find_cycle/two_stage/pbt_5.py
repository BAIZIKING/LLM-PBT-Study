from hypothesis import given, strategies as st
import networkx

# Define strategies for graph generation with limitations to avoid large inputs
nodes = st.integers(min_value=0, max_value=100)  # Limit number of nodes
edges = st.tuples(nodes, nodes).filter(lambda x: x[0] != x[1])  # Avoid self-loops

# Strategies for directed/undirected and various orientations
graph_types = st.sampled_from([nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph])
orientations = st.sampled_from([None, 'original', 'reverse', 'ignore'])


@given(graph_types, nodes, edges, orientations)
def test_networkx_find_cycle_length(graph_type, num_nodes, edge_list, orientation):
    G = graph_type()
    G.add_nodes_from(range(num_nodes))
    G.add_edges_from(edge_list)

    try:
        cycle = nx.find_cycle(G, orientation=orientation)
        assert len(cycle) >= 2  # Cycle must have at least 2 edges
    except nx.NetworkXNoCycle:
        pass  # No cycle exists, property vacuously holds

@given(graph_types, nodes, edges, orientations)
def test_networkx_find_cycle_start_end(graph_type, num_nodes, edge_list, orientation):
    G = graph_type()
    G.add_nodes_from(range(num_nodes))
    G.add_edges_from(edge_list)

    try:
        cycle = nx.find_cycle(G, orientation=orientation)
        start_node, _ = cycle[0]
        _, end_node = cycle[-1]
        assert start_node == end_node  # Start and end nodes must be the same
    except nx.NetworkXNoCycle:
        pass 

@given(graph_types, nodes, edges, orientations)
def test_networkx_find_cycle_unique_edges(graph_type, num_nodes, edge_list, orientation):
    G = graph_type()
    G.add_nodes_from(range(num_nodes))
    G.add_edges_from(edge_list)

    try:
        cycle = nx.find_cycle(G, orientation=orientation)
        assert len(set(cycle)) == len(cycle)  # Check for unique edges
    except nx.NetworkXNoCycle:
        pass

@given(graph_types, nodes, edges, orientations)
def test_networkx_find_cycle_connectivity(graph_type, num_nodes, edge_list, orientation):
    G = graph_type()
    G.add_nodes_from(range(num_nodes))
    G.add_edges_from(edge_list)

    try:
        cycle = nx.find_cycle(G, orientation=orientation)
        for i in range(len(cycle) - 1):
            _, v = cycle[i]
            w, _ = cycle[i + 1]
            assert v == w  # Check connectivity between consecutive edges 
    except nx.NetworkXNoCycle:
        pass 

@given(st.data())
def test_networkx_find_cycle_direction(data):
    # Generate directed graph with controlled edge directions
    num_nodes = data.draw(st.integers(min_value=3, max_value=7))
    edge_list = data.draw(
        st.lists(st.tuples(st.integers(min_value=0, max_value=num_nodes - 1), 
                           st.integers(min_value=0, max_value=num_nodes - 1)),
                  min_size=num_nodes, unique=True)
    )
    G = nx.DiGraph()
    G.add_nodes_from(range(num_nodes))
    G.add_edges_from(edge_list)

    for orientation in ['original', 'reverse']:
        try:
            cycle = nx.find_cycle(G, orientation=orientation)
            for edge in cycle:
                u, v, direction = edge
                if orientation == 'original':
                    assert G.has_edge(u, v)
                elif orientation == 'reverse':
                    assert G.has_edge(v, u)
                assert direction in ['forward', 'reverse']  # Check direction consistency
        except nx.NetworkXNoCycle:
            pass 

# End program