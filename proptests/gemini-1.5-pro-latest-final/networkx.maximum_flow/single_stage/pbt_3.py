from hypothesis import given, strategies as st
import networkx as nx

# Define strategies for graph generation
def graph_strategy():
    # Generate graphs with varying sizes and densities
    graph_size = st.integers(min_value=0, max_value=20)
    edge_probability = st.floats(min_value=0.0, max_value=1.0)
    return st.graphs(graph_size, edge_probability, directed=True)

def capacity_strategy():
    # Generate capacities as integers or floats, including 0 and "infinite"
    return st.one_of(
        st.integers(min_value=0), 
        st.floats(allow_nan=False, allow_infinity=False),
        st.just(float("inf"))
    )

# Define strategies for source/sink and flow_func
node_strategy = st.integers()
flow_func_strategy = st.sampled_from([None, nx.algorithms.flow.shortest_augmenting_path])

# Summary: Generates random directed graphs, source/sink nodes, and flow algorithms
@given(graph=graph_strategy(), capacity=st.dictionaries(st.edges(), capacity_strategy()),
       source=node_strategy, target=node_strategy, flow_func=flow_func_strategy)
def test_networkx_maximum_flow(graph, capacity, source, target, flow_func):
    # Set capacity attribute for edges
    nx.set_edge_attributes(graph, capacity, "capacity")
    
    try:
        flow_value, flow_dict = nx.maximum_flow(graph, source, target, flow_func=flow_func)

        # Check flow conservation
        outflow_sum = sum(flow_dict[source].get(v, 0) for v in graph.neighbors(source))
        inflow_sum = sum(flow_dict[u].get(target, 0) for u in graph.predecessors(target))
        assert outflow_sum == inflow_sum == flow_value
        
        # Check capacity constraints
        for u, v, data in graph.edges(data=True):
            assert 0 <= flow_dict[u][v] <= data["capacity"]
        
        # Check skew symmetry
        for u, v in graph.edges():
            assert flow_dict[u][v] == -flow_dict[v].get(u, 0)
    except nx.NetworkXError:
        assert isinstance(graph, (nx.MultiGraph, nx.MultiDiGraph))
    except nx.NetworkXUnbounded:
        # Check for infinite capacity paths (implementation-dependent)
        pass
    
# End program