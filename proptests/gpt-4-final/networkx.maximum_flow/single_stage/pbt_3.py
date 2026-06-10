from hypothesis import given, strategies as st
from hypothesis.networkx import graph_builder, nodes, edges
import networkx as nx

@given(graph_builder(nodes=nodes(integers(min_value=0, max_value=50)), 
                     edges=edges(integers(min_value=0, max_value=10), 
                                 key=just('capacity'),
                                 attributes=dict(capacity=integers(min_value=0, max_value=10)))),
       data=st.data()
      )

def test_maximum_flow(G, data):
    # Ensure we have more than one node to avoid source equals sink error
    if len(G.nodes()) < 2:
        return
    # Set up source and sink nodes
    _s = data.draw(st.sampled_from(list(G.nodes())))
    _t = data.draw(st.sampled_from([node for node in G.nodes() if node != _s]))
    
    try:
        # Get max flow value and flow dictionary
        flow_value, flow_dict = nx.maximum_flow(G, _s, _t)
        # Check types of max_flow_func output
        assert isinstance(flow_value, (int, float))
        assert isinstance(flow_dict, dict)
        # Check max flow value equals sum of flows from source and sum of flows to sink
        assert flow_value == sum(flow_dict[_s].values())
        assert flow_value == sum(flow_dict[node][_t] for node in flow_dict if _t in flow_dict[node])
    except nx.NetworkXError:
        # Ignore error raised for Multigraph and Multidigraph
        pass
    except nx.NetworkXUnbounded:
        # Ignore error raised for infinite path
        pass
# End program