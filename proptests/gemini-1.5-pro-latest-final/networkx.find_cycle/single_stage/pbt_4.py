from hypothesis import given, strategies as st
import networkx as nx

# Summary: This strategy aims to generate a wide variety of inputs for the networkx.find_cycle function, 
# including edge cases, to thoroughly test its behavior. The approach involves:
# 1. Graph Types: Generate diverse graph types including directed, undirected, multigraphs, and mixed combinations.
# 2. Node and Edge Counts: Vary the number of nodes and edges to cover sparse and dense graphs.
# 3. Source Node: Test with both specified source nodes and the default behavior of choosing a source automatically.
# 4. Orientation: Explore different orientation settings ('original', 'reverse', 'ignore', None) to cover various traversal directions. 
@given(st.data())
def test_networkx_find_cycle(data):
    # Generate graph types randomly
    graph_types = [nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph]
    graph_type = data.draw(st.sampled_from(graph_types))
    
    # Generate number of nodes and edges
    num_nodes = data.draw(st.integers(min_value=2, max_value=20))  # Adjust range as needed
    num_edges = data.draw(st.integers(min_value=num_nodes-1, max_value=num_nodes*(num_nodes-1)/2))  # Ensure enough edges for potential cycles

    # Create graph with random edges
    G = graph_type()
    G.add_nodes_from(range(num_nodes))
    edges = data.draw(st.sets(st.tuples(st.integers(min_value=0, max_value=num_nodes-1), st.integers(min_value=0, max_value=num_nodes-1)), min_size=num_edges, max_size=num_edges))
    G.add_edges_from(edges)

    # Generate source node (or None for default behavior)
    source = data.draw(st.one_of(st.none(), st.integers(min_value=0, max_value=num_nodes-1)))

    # Generate orientation options
    orientations = [None, 'original', 'reverse', 'ignore']
    orientation = data.draw(st.sampled_from(orientations))

    # Call find_cycle and check properties
    try:
        cycle = nx.find_cycle(G, source=source, orientation=orientation)

        # Property 1: Verify the cycle is indeed a cycle (forms a closed loop)
        assert cycle[0][0] == cycle[-1][-2]  # Check if the first and last nodes are the same

        # Property 2 (for directed graphs): Check if edge directions are consistent with the chosen orientation
        if G.is_directed() and orientation is not None:
            for u, v, direction in cycle:
                if orientation == 'reverse':
                    assert G.has_edge(v, u)
                elif orientation == 'original':
                    assert G.has_edge(u, v)

    except nx.NetworkXNoCycle:
        # If no cycle found, ensure the graph is acyclic
        assert nx.is_directed_acyclic_graph(G) if G.is_directed() else nx.is_forest(G)

# End program