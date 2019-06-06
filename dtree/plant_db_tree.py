from buildtree import *


def encode_node(tree, node_list, node_id, feature_dict):
    if isinstance(tree, decisionnode1):
        node_dict = {"id": node_id, "children":{}, "q": None, "r": None, "fname": None}
        my_id = node_id - 1

        node_list.append(node_dict)
        node_id += 1

        if tree.children != None and len(tree.children) > 1:
            for key,val in tree.children.items():
                node_list[my_id]["children"][key] = node_id
                node_id = encode_node(val, node_list, node_id, feature_dict)

        if tree.children is not None:
            node_list[my_id]["q"] = feature_dict[tree.col]
        if tree.results is not None:
            node_list[my_id]["r"] = tree.results
        if tree.fname is not None:
            node_list[my_id]["fname"] = feature_dict[tree.fname]

        return node_id


def get_children(parent_node, node_list, feature_by_question):
    has_children = (len(parent_node["children"])>0)
    if not has_children:
        return None
    children = []
    for key, val in parent_node["children"].items():
        child_node = get_node_by_id(node_list, val)
        if child_node:
            new_child = {}
            new_child["name"] = feature_by_question.get(child_node["q"],child_node["q"])
            grandchildren = get_children(child_node, node_list, feature_by_question)
            if grandchildren is not None:
                new_child["children"] = grandchildren
            else: #leaf node
                taxa_list = list(child_node["r"].items())
                # print(type(taxa_list))
                new_child["name"] = '\n'.join(map(lambda x: x[0], taxa_list))
            full_name = '(A:' + str(key)[:14] + ').  ' + str(new_child["name"])
            new_child["name"] = full_name
            children.append(new_child)
    return children




def get_node_by_id(node_list, id):
    for node in node_list:
        if node["id"]==id:
            return node
    return None


def build_json_d3_visualization(node_list, feature_by_question):
    tree = {}
    root = get_node_by_id(node_list,1)
    if not root:
        print ("root not found")
        return tree
    tree["name"] = feature_by_question.get(root["q"],root["q"])
    children = get_children(root, node_list,feature_by_question)
    if children is not None:
        tree["children"] = children
    return tree

