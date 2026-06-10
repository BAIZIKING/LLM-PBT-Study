from hypothesis import given, strategies as st
from networkx import DiGraph, add_path, lowest_common_ancestor

# generate random directed graphs
def gen_graphs():
    return st.builds(add_path, 
                     st.builds(DiGraph), 
                     st.lists(st.integers(min_value=0, max_value=10)))

@given(G=gen_graphs(), data=st.data())
def test_lowest_common_ancestor(G, data):
  nodes = [data.draw(st.integers(min_value=0, max_value=10)) for _ in range(2)]
  result = lowest_common_ancestor(G, nodes[0], nodes[1])

  # If the nodes are equal, the return value should be the same node.
  if nodes[0] == nodes[1]:
      assert result == nodes[0]
  # If node1 is ancestor of node2 or vice versa, the return should be the ancestor.
  elif nodes[0] in G.predecessors(nodes[1]):
      assert result == nodes[0]
  elif nodes[1] in G.predecessors(nodes[0]):
      assert result == nodes[1]
  else:
      assert result in G.predecessors(nodes[0]) and result in G.predecessors(nodes[1])