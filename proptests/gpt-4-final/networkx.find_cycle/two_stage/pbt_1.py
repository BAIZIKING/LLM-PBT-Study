from hypothesis import given, strategies as st
import networkx as nx

# Define a strategy to generate input graphs
graphs = st.builds(nx.gnp_random_graph, st.integers(1, 10), st.floats(0, 1))

@given(graphs, st.sampled_from([None, 'original', 'reverse', 'ignore']))
def test_find_cycle(graph, orientation):
    try:
        cycle = nx.find_cycle(graph, orientation=orientation)

        # Cycle Existence
        assert cycle, "returned cycle should not be empty"

        # Cycle Structure
        visited = set()
        for u, v, *direction in cycle:
            assert u not in visited, "node should not be visited twice in the cycle"
            visited.add(u)
        assert cycle[0][0] == cycle[-1][1], "should go back to the start node"
        
        # Return Value Type
        for edge in cycle:
            assert type(edge) in [tuple, ], "Each edge should be a tuple"
            if orientation is not None:
                assert len(edge) in [3, 4], "Each edge should have 3 elements (for graphs) or 4 (for multigraphs)"
            else:
                assert len(edge) in [2, 3], "Each edge should have 2 elements (for graphs) or 3 (for multigraphs)"

        # Traversal Direction
        if orientation is not None:
            for u, v, key, direction in cycle:
                assert direction in ['forward', 'reverse'], "direction should be forward or reverse"

    except nx.exception.NetworkXNoCycle:
        # Exception when no cycle is found
        pass

# End program