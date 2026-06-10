from hypothesis import given, strategies as st
import networkx as nx

@given(st.integers(min_value=2, max_value=20), st.lists(st.integers(), min_size=2, max_size=20), st.sampled_from([None, 'original', 'reverse', 'ignore']))
def test_find_cycle_properties(n_nodes, edge_vals, orientation):

    # Create random directed Graph
    G = nx.DiGraph()
    G.add_nodes_from(range(n_nodes))
    edges_list = [[edge_vals[i], edge_vals[i+1]] for i in range(len(edge_vals)-1)]
    G.add_edges_from(edges_list)

    # Try Find Cycle
    try:
        cycle = list(nx.find_cycle(G, orientation=orientation))

        # Check properties
        # Property 1: Output is list of tuples
        assert isinstance(cycle, list)
        for item in cycle:
            assert isinstance(item, tuple)

        # Property 3: Check the orientation of returned edges
        if orientation in ['original', 'reverse', 'ignore']:
            for edge in cycle:
                assert 'forward' in edge or 'reverse' in edge

        # Property 4: Check edge frequency in case of directed graph
        if orientation in ['original', 'reverse']:
            edge_frequency = {edge: cycle.count(edge) for edge in cycle}
            for frequency in edge_frequency.values():
                assert frequency == 1

    # Handle no cycle exception
    except nx.NetworkXNoCycle:
        pass

# End program
