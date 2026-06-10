from hypothesis import given, strategies as st
import networkx as nx

# Summary: The generation strategy aims to create diverse input graphs for testing networkx.maximum_flow. 
# It varies the number of nodes and edges, edge capacities, presence of self-loops, and directionality (DiGraph or Graph).
# Edge cases include graphs with no edges, single-node graphs, and graphs with infinite capacity edges.
@given(st.data())
def test_networkx_maximum_flow(data):
    # Generate graph parameters
    num_nodes = data.draw(st.integers(min_value=0, max_value=20))  # Varying number of nodes
    num_edges = data.draw(st.integers(min_value=0, max_value=num_nodes*(num_nodes-1)))  # Varying number of edges
    is_directed = data.draw(st.booleans())  # Generate both DiGraphs and Graphs

    # Create graph based on generated parameters
    if is_directed:
        G = nx.DiGraph()
    else:
        G = nx.Graph()
    G.add_nodes_from(range(num_nodes))

    # Generate edges with varying capacities and potential self-loops
    for _ in range(num_edges):
        u = data.draw(st.integers(min_value=0, max_value=num_nodes-1))
        v = data.draw(st.integers(min_value=0, max_value=num_nodes-1))
        capacity = data.draw(st.floats(allow_infinity=True, allow_nan=False))  # Allow infinite capacities
        G.add_edge(u, v, capacity=capacity)

    # Generate source and sink nodes within the graph
    _s = data.draw(st.integers(min_value=0, max_value=num_nodes-1))
    _t = data.draw(st.integers(min_value=0, max_value=num_nodes-1))

    # Properties to check based on the API documentation
    try:
        flow_value, flow_dict = nx.maximum_flow(G, _s, _t)

        # 1. Flow value should be non-negative
        assert flow_value >= 0

        # 2. Flow through each edge should not exceed capacity
        for u, v, data in G.edges(data=True):
            assert flow_dict[u][v] <= data['capacity']

        # 3. Flow conservation: inflow == outflow for all nodes except source and sink
        for node in G.nodes():
            if node not in (_s, _t):
                inflow = sum(flow_dict[u][node] for u in G.predecessors(node))
                outflow = sum(flow_dict[node][v] for v in G.successors(node))
                assert inflow == outflow

    except nx.NetworkXUnbounded:
        # Expected exception for graphs with infinite-capacity paths
        pass
# End program