from buildtree import *
from plant_db_tree import *
from displaytree import *
import json

NUMBER_COLS = []
NUM_COLS = 11  # 11 or 23
MAX_DEPTH = 20


def read_tsv(filename):
    input_f = open(filename, encoding="latin1")
    rows = []
    feature_dict = {}

    header = True
    for line in input_f:
        arr = line.rstrip().split('\t')
        # Get a list of header
        if header:
            for i in range(len(arr)):
                feature_dict[i] = arr[i]
                header = False
        else:
            for i in range(len(arr)):
                try:
                    arr[i] = int(arr[i])
                except ValueError:
                    if i in NUMBER_COLS and arr[i] != MISSINGCHAR:
                        arr = []
                        break
            if len(arr) != NUM_COLS:
                continue
            rows.append(arr)
    input_f.close()
    return rows, feature_dict


leaf_classes_arr = []


# Get a list of leaf classes
def get_leaf_classes_arr(json_object):
    inner_dic = json_object['children']
    for element in inner_dic:
        try:
            get_leaf_classes_arr(element)
        except KeyError:
            leaf_classes_arr.append(element["name"])


# Get the max number of classes per leaf and the average number of classes per leaf
def test_leaves():
    class_num_per_leaf_arr = []
    for leaf_index in range(len(leaf_classes_arr)):
        class_arr = leaf_classes_arr[leaf_index].split("\n")

        class_num_per_leaf_arr.append(len(class_arr))

    return max(class_num_per_leaf_arr), sum(class_num_per_leaf_arr) / len(class_num_per_leaf_arr)


if __name__ == "__main__":
    print("Reading in file...")
    # flower_table: list of list of feature rows, flower_features: list of attributes
    flower_table,flower_features = read_tsv("d_flower_data.tsv")
    print("{} observations!".format(len(flower_table)))
    print("Building tree...")
    feature_by_question = {}
    for q in flower_features:
        feature_by_question[q] = q  # list of keys (num) associated with features

    tree = buildtree1(flower_table, NUM_COLS - 1, 0, MAX_DEPTH, [], min_gain=0.01)  # build tree

    node_list = []
    encode_node(tree, node_list, 1, flower_features)
    json_object = build_json_d3_visualization(node_list, feature_by_question)

    # Test leaves
    get_leaf_classes_arr(json_object)
    max_num_of_classes_per_leaf, ave_num_of_classes_per_leaf = test_leaves()
    print("The max number of classes per leaf is:", max_num_of_classes_per_leaf)
    print("The average number of classes per leaf is:", ave_num_of_classes_per_leaf)

    json_output = open("test_tree.json", 'w')
    json.dump(json_object, json_output)
    json_output.close()

    node_output = open("node_list.json", "w")
    json.dump(node_list, node_output)
    node_output.close()