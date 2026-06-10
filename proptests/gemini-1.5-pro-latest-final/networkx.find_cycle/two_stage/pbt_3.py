from hypothesis import given, strategies as st
import networkx

# Define graph generation strategy with size limit
def graph_strategy(max_nodes=10, max_edges=20):
    return st.graphs(
        st.integers(min_value=0, max_value=max_nodes-1),
        st.tuples(st.integers(min_value=0, max_value=max_nodes-1), st.integers(min_value=0, max_value=max_nodes-1)),
        max_edges=max_edges
    )

# Orientation strategy
orientation_strategy = st.sampled_from(['original', 'reverse', 'ignore', None])

@given(graph=graph_strategy(), source=st.integers(), orientation=orientation_strategy)
def test_networkx_find_cycle_cycle_property(graph, source, orientation):
    try:
        cycle = nx.find_cycle(graph, source, orientation)
        # Check if first and last node are the same
        assert cycle[0][0] == cycle[-1][-2]
        # Check if all edges are unique
        assert len(set(cycle)) == len(cycle)
    except nx.NetworkXNoCycle:
        pass  # No cycle found, property vacuously holds

@given(graph=graph_strategy(), source=st.integers(), orientation=orientation_strategy)
def test_networkx_find_cycle_connectivity_property(graph, source, orientation):
    try:
        cycle = nx.find_cycle(graph, source, orientation)
        if orientation == 'original':
            for u, v, *_ in cycle:
                assert graph.has_edge(u, v)
        else:
            for u, v, *_ in cycle:
                assert graph.has_edge(u, v) or graph.has_edge(v, u)
    except nx.NetworkXNoCycle:
        pass 

@given(graph=graph_strategy(max_nodes=5), source=st.integers(), orientation=st.sampled_from(['reverse', 'ignore']))
def test_networkx_find_cycle_orientation_property(graph, source, orientation):
    try:
        cycle = nx.find_cycle(graph, source, orientation)
        if orientation == 'reverse':
            for u, v, *_ in cycle:
                assert graph.has_edge(v, u) 
    except nx.NetworkXNoCycle:
        pass  

@given(graph=graph_strategy(min_nodes=3), source=st.integers(), orientation=orientation_strategy)
def test_networkx_find_cycle_length_property(graph, source, orientation):
    try:
        cycle = nx.find_cycle(graph, source, orientation)
        assert len(cycle) >= 3 
    except nx.NetworkXNoCycle:
        pass  

@given(graph=graph_strategy(), source=st.integers(), orientation=orientation_strategy)
def test_networkx_find_cycle_determinism_property(graph, source, orientation):
    try:
        cycle1 = nx.find_cycle(graph, source, orientation)
        cycle2 = nx.find_cycle(graph, source, orientation)
        assert cycle1 == cycle2
    except nx.NetworkXNoCycle:
        pass  
# End Program