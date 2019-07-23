from decision_tree import *
import json
import time
import itertools

NUM_COLS = 0  # Number of columns in the dataset
CONFIG_FILE = "config.txt"


def read_data(filename):
    global NUM_COLS
    input_f = open(filename, encoding="UTF-8")
    rows = []
    feature_dict = []
    row_id = 0
    header = True
    for line in input_f:
        row_id += 1
        arr = line.rstrip().split('\t')
        # Get a list of header
        if header:
            NUM_COLS = len(arr)
            for i in range(len(arr)):
                feature_dict.append(arr[i])
            header = False
        else:
            if len(arr) < NUM_COLS:
                print("Error on row", row_id, "Not enough columns!")
                exit(1)
            for i in range(len(arr)):
                try:
                    arr[i] = int(arr[i].strip())
                except ValueError:
                    try:
                        arr[i] = float(arr[i].strip())
                    except ValueError:
                        arr[i] = arr[i].strip()
                        pass

            row = arr[0:NUM_COLS]
            labels = arr[NUM_COLS:]

            rows.append([row]+[labels])

    input_f.close()
    return rows, feature_dict


def get_config_property(key):
    f = open(CONFIG_FILE)
    for line in f:
        line = line.strip()
        a = line.split('=')
        if a[0] == key:
            f.close()
            return a[1]

    f.close()
    print("No value for key", key)
    return None


# Find number of labels on leaves and branch depths, which are put into leaf_label_count_arr, depth_arr respectively
def leaf_label_and_depth_count(current_node, leaf_label_count_arr, depth_arr, current_depth=0):
    # Leaf
    if current_node.results and len(current_node.results) > 0:
        if len(uniquecounts(current_node.results,current_node.class_id).keys()) > 1:
            print(uniquecounts(current_node.results, current_node.class_id))
        # Append the depth when reaching leaf nodes
        depth_arr.append(current_depth)
        leaf_label_count_arr.append(len(uniquecounts(current_node.results,
                                                     current_node.class_id).keys()))
        return

    # Compute the depth of each sub-branch
    current_depth += 1

    leaf_label_and_depth_count(current_node.tb, leaf_label_count_arr, depth_arr, current_depth)
    leaf_label_and_depth_count(current_node.fb, leaf_label_count_arr, depth_arr, current_depth)


def get_max_and_ave(count_arr):
    return max(count_arr), sum(count_arr)/len(count_arr)


def write_json(json_tree):
    with open('test_tree.json', 'w') as outfile:
        json.dump(json_tree, outfile)


if __name__ == "__main__":
    print("Reading in file...")
    # flower_table: list of list of feature rows, flower_features: list of attributes
    flower_table, flower_features = read_data("d_flower_data_full.tsv")
    label_col_index = get_config_property("class_column")  # return the level index number
    try:
        label_col_index = int(label_col_index)
    except:
        print("Invalid value for key", "'class_column'")
        exit(1)
    # delimited_flower_table = flatten_alt_values(flower_table)
    print("{} observations, {} features".format(len(flower_table), NUM_COLS))

    # flower_features = ["Q1", "Q2", "Q3", "Q4", "Q5"]
    # flower_table = [
    #     [[2, "?", '?', "a || b", "x"], ["class1", "top class3"]],
    #     [[2, "b", 1, "b", "x"], ["class1", "top class4"]],
    #     [[3, "b", 2, "c", "y"], ["class1", "top class3"]],
    #     [[3, "a || b", 5, "a", "x"], ["class2", "top class2"]],
    #     [['?', "a", 3, "?", "x"], ["class2", "top class2"]],
    #     [[3, "b", 4, "a || b || c", "?"], ["class2", "top class4"]],
    #     [[2, "b", 2, "c", "x"], ["class2", "top class2"]],
    #     [[4, "b", 3, "b", "z"], ["class2", "top class2"]],
    #     [[4, "a || b || c", 6, "c || d", "x || z"], ["class2", "top class4"]],
    #     [['?', "a", 5, "d", "?"], ["class2", "top class3"]]
    # ]
    # label_col_index = 1
    # print("{} observations, {} features".format(len(flower_table), NUM_COLS))

    print("Building tree...")
    min_gain = float(get_config_property("min_gain"))

    col_not_used = list(range(len(flower_features)))

    start_time = time.time()
    tree = build_tree(flower_table, flower_features, label_col_index, min_gain, col_not_used)  # build tree
    elapsed_time = time.time() - start_time
    print('Time used to build the tree {} seconds'.format(round(elapsed_time)))

    attribute_not_used = [flower_features[attr_index] for attr_index in col_not_used]

    print('Col id not used: ', col_not_used)
    print('Attributes not used: ', attribute_not_used)
    print('Number of attributes not used: ', len(attribute_not_used))

    # print_tree(tree)

    leaf_label_count_arr = []  # a list of number of leaf labels
    depth_arr = []  # a list of branch depths

    leaf_label_and_depth_count(tree, leaf_label_count_arr, depth_arr, False)

    # Get max number of labels on leaves and average number of labels
    max_leaf_lab_num, ave_leaf_lab_num = get_max_and_ave(leaf_label_count_arr)
    # Get max depth and average depth of the tree
    max_dep, ave_depth = get_max_and_ave(depth_arr)

    print("The max depth of the tree is: ", max_dep)
    print("The average depth of the tree is: ", ave_depth)
    print("The max number of labels is: ", max_leaf_lab_num)
    print("The average number of classes per leaf is: ", ave_leaf_lab_num)
    json_tree = {}
    construct_json(tree, json_tree)
    write_json(json_tree)
