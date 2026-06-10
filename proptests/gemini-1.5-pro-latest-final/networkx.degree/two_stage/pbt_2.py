from hypothesis import given, strategies as st
import networkx as nx

# Define strategies for generating graphs and node lists
graph_strategy = st.graphs(st.integers(min_value=0, max_value=100), st.edges(max_size=100))
node_strategy = st.lists(st.integers(min_value=0, max_value=100), max_size=100)

@given(graph_strategy, node_strategy)
def test_missing_node(graph, nodes):
    for node in nodes:
        if node not in graph:
            assert node not in nx.degree(graph)
# End program