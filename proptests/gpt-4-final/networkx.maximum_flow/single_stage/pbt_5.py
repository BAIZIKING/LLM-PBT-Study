import networkx as nx
from hypothesis import given, strategies as st

@given(
    st.dictionaries(
        st.tuples(st.integers(min_value=0, max_value=20), st.integers(min_value=0, max_value=20)),
        st.floats(min_value=0.0, max_value=100.0),
        min_size=2
    )
)
def test_networkx_maximum_flow(graph):
    flowG = nx.DiGraph()
    for edge, capacity in graph.items():
        flowG.add_edge(*edge, capacity=capacity)
    
    # Select random nodes for source and target
    _s, _t = st.sampled_from(flowG.nodes()).example(), st.sampled_from(flowG.nodes()).example()
    
    try:
        flow_value, flow_dict = nx.maximum_flow(flowG, _s, _t)

        assert isinstance(flow_value, (int, float))
        assert flow_value >= 0

        for u, inner_dict in flow_dict.items():
            for v, flow_value in inner_dict.items():
                capacity = flowG[u][v]['capacity']

                assert flow_value >= 0
                assert flow_value <= capacity

        assert sum(flow_dict[_s].values()) == flow_value

    except nx.NetworkXError:
        pass  # The test should pass if the algorithm raises a NetworkXError

    except nx.NetworkXUnbounded:
        pass  # The test should pass if the algorithm raises a NetworkXUnbounded