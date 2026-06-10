from hypothesis import given, strategies as st
import networkx as nx

@given(st.data())
def test_find_cycle(data):
    # Generate a list of edges
    edges = data.draw(st.lists(st.tuples(st.integers(), st.integers())))
    # Generate a random source
    source = data.draw(st.one_of(st.none(), st.integers(min_value=min(edges)[0], max_value = max(edges)[0])))
    # Generate a random orientation
    orientation = data.draw(st.sampled_from(['original', 'reverse', 'ignore', None]))

    # Construct a graph
    G = nx.DiGraph(edges)

    try:
        # Find a cycle
        cycle = nx.find_cycle(G, source, orientation)
        
        # If a cycle is found, it must be a list of directed edges
        assert isinstance(cycle, list)
        if orientation is not None:
            # If orientation is not None, an edge in the cycle must have direction of traversal
            assert len(cycle[0]) == 3
    except nx.NetworkXNoCycle:
        # If no cycle was found, an NetworkXNoCycle exception must be raised
        pass