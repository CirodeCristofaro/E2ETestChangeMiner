from apted import APTED, PerEditOperationConfig


def algo_apted(root1, root2, weight_elimination, weight_added, weight_renamed):
    apted = APTED(root1, root2, PerEditOperationConfig(weight_elimination, weight_added, weight_renamed))
    distance = apted.compute_edit_distance()
    mapping = apted.compute_edit_mapping()
    return distance, mapping


def print_distance(distance, mapping):
    for node1, node2 in mapping:
        print(f"Node1: {node1}, Node2: {node2}")
    remove = 0
    insert = 0
    rename = 0
    for i, (node1, node2) in enumerate(mapping):
        if node1 is None:
            print(f"Operation {i + 1}: Insertion of Node2: {node2}")
            insert += 1
        elif node2 is None:
            print(f"Operation {i + 1}: Deletion of Node1: {node1}")
            remove += 1
        elif node1.name != node2.name:
                print(f"Operation {i + 1}: Rename of Node1: {node1} to Node2: {node2}")
                rename += 1

    tot = (remove * .2) + (insert * .3) + (rename * .4)
    print(f"Tot: {tot} , Remove: {remove} , Inserted: {insert}, Renamed: {rename}")
    print(f"Edit Distance: {distance}")

def tree_to_tree_node( parser,node,src):
    node_text = parser.extract_text_from_node(node,src)
    if node.child_count == 0:  # Nodo foglia
        return TreeNode(node_text)
    else:
        children = [tree_to_tree_node(parser,child,src) for child in node.children]
        return TreeNode(node_text, children)

class TreeNode:
    def __init__(self, name, children=None):
        self.name = name
        self.children = children if children else []

    def __repr__(self):
        return f"TreeNode(name={self.name}, children={len(self.children)})"
