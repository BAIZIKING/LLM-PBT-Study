from hypothesis import given, strategies as st
import networkx as nx

@given(st.data())
def test_same_node(data):
    G = nx.DiGraph()
    node = data.draw(st.integers())
    G.add_node(node)
    assert nx.lowest_common_ancestor(G, node, node) == node

@given(st.data())
def test_node1_ancestor_of_node2(data):
    G = nx.DiGraph()
    node1 = data.draw(st.integers())
    node2 = data.draw(st.integers())
    G.add_edge(node1, node2)
    assert nx.lowest_common_ancestor(G, node1, node2) == node1

@given(st.data())
def test_node2_ancestor_of_node1(data):
    G = nx.DiGraph()
    node1 = data.draw(st.integers())
    node2 = data.draw(st.integers())
    G.add_edge(node2, node1)
    assert nx.lowest_common_ancestor(G, node1, node2) == node2

@given(st.data())
def test_no_common_ancestors(data):
    G = nx.DiGraph()
    node1 = data.draw(st.integers())
    node2 = data.draw(st.integers())
    G.add_node(node1)
    G.add_node(node2)
    assert nx.lowest_common_ancestor(G, node1, node2) is None

@given(st.data())
def test_returned_ancestor(data):
    G = nx.DiGraph()
    node1 = data.draw(st.integers())
    node2 = data.draw(st.integers())
    ancestor = data.draw(st.integers())
    G.add_edge(ancestor, node1)
    G.add_edge(ancestor, node2)
    assert nx.lowest_common_ancestor(G, node1, node2) == ancestor
# End program