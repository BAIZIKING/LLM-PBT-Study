from hypothesis import given, strategies as st
import networkx as nx

@given(st.data())
def test_monotonicity(data):
    G = data.draw(st.graphs(directed=True, max_nodes=10))
    _s = data.draw(st.sampled_from(list(G.nodes)))
    _t = data.draw(st.sampled_from([n for n in G.nodes if n != _s]))
    capacity = {e: data.draw(st.floats(min_value=0, max_value=1000)) for e in G.edges}
    nx.set_edge_attributes(G, capacity, 'capacity')

    flow_value1, _ = nx.maximum_flow(G, _s, _t)

    increased_edge = data.draw(st.sampled_from(list(G.edges)))
    G[increased_edge[0]][increased_edge[1]]['capacity'] += data.draw(st.floats(min_value=0, max_value=1000))

    flow_value2, _ = nx.maximum_flow(G, _s, _t)

    assert flow_value2 >= flow_value1
# End program