from buildtree import *
from plant_db_tree import *
from displaytree import *
import json

NUMBER_COLS = []
NUM_COLS = 23


def read_tsv(filename):
    input_f = open(filename, encoding="latin1")
    rows = []
    feature_dict = {}

    header = True
    for line in input_f:
        arr = line.rstrip().split('\t')
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


if __name__ == "__main__":
    print("Reading in file...")
    flower_table, flower_features = read_tsv("../flower_data/d_flower_data.tsv")
    print("{} observations!".format(len(flower_table)))
    print("Building tree...")

    feature_by_question = {}
    for q in flower_features:
        feature_by_question[q] = q

    tree = buildtree1(flower_table, NUM_COLS - 1, [], min_gain=0.01)

    node_list = []
    encode_node(tree, node_list, 1, flower_features)
    json_object = build_json_d3_visualization(node_list, feature_by_question)
    json_output = open("test_tree.json", 'w')
    json.dump(json_object, json_output)
    json_output.close()

    node_output = open("node_list.json", "w")
    json.dump(node_list, node_output)
    node_output.close()
