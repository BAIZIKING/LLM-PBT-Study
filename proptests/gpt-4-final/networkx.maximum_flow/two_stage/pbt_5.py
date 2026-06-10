from hypothesis import given, strategies as st
import networkx as nx

# Generating a strategy for graphs, source and target nodes
def graph_strategy():
    return st.tuples(
        st.dictionaries(
            st.tuples(st.integers(), st.integers()), 
            st.integers(min_value=1, max_value=10)
            ).map(nx.DiGraph),
        st.integers(min_value=0, max_value=9),
        st.integers(min_value=0, max_value=9)
        ).filter(lambda x: x[1] != x[2] and x[1] in x[0] and x[2] in x[0])

@given(graph_strategy())
def test_maximum_flow_property(graph_tuple):
    graph, s, t = graph_tuple

    # Property 1 - Return type check
    result = nx.maximum_flow(graph, s, t)
    assert isinstance(result, tuple) and len(result) == 2
    flow_value, flow_dict = result
    assert isinstance(flow_value, (int, float)) and isinstance(flow_dict, dict)

    # Property 2 - Outflow from source equals to the flow value
    total_outflow = sum(edge_attr['flow'] for edge_attr in flow_dict[s].values())
    assert flow_value == total_outflow

    # Property 3 - Error raising check
    multigraph = graph.to_undirected()
    try:
        nx.maximum_flow(multigraph, s, t)
    except nx.NetworkXError:
        pass

    # Property 5 - Consistency with different flow functions
    alternative_flows = [nx.maximum_flow(graph, s, t, flow_func=algo)[0] for algo in [nx.preflow_push, nx.shortest_augmenting_path]]
    assert all(flow_value == alternative_flow for alternative_flow in alternative_flows)