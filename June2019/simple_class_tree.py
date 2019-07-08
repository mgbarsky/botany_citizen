from decision_tree import *
import json
import itertools


NUM_COLS = 11  # Number of columns in the dataset
CONFIG_FILE = "config.txt"


def read_data(filename):
    global NUM_COLS
    input_f = open(filename, encoding="UTF-8")
    rows = []
    feature_dict = []
    row_id = 0
    NUM_COLS = 0
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
        leaf_label_count_arr.append(len(uniquecounts(current_node.results,
                                                     label_col_index).keys()))
        return

    # Compute the depth of each sub-branch
    current_depth += 1
    depth_arr.append(current_depth)

    for child in current_node.children:
        leaf_label_and_depth_count(child, leaf_label_count_arr, depth_arr, current_depth)


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
    #     [[2, "?", '?', "a or b", "x"], ["class1", "top class3"]],
    #     [[4, "b", 1, "b", "x"], ["class1", "top class4"]],
    #     [[3, "b", 3, "c", "y"], ["class1", "top class3"]],
    #     [[20, "a or b", 20, "a", "x"], ["class2", "top class2"]],
    #     [['?', "a", 5, "?", "x"], ["class2", "top class2"]],
    #     [[8, "b", 2, "a or b or c", "?"], ["class2", "top class4"]],
    #     [[10, "b", 3, "c", "x"], ["class2", "top class2"]],
    #     [[10, "b", 6, "b", "z"], ["class2", "top class2"]],
    #     [[15, "a or b or c", 10, "c or d", "x or z"], ["class2", "top class4"]],
    #     [['?', "a", 12, "d", "?"], ["class2", "top class3"]],
    # ]
    # label_col_index = ask_level_input(flower_table)  # return the level index    number

    print("Building tree...")
    min_gain = float(get_config_property("min_gain"))
    tree = build_tree(None, flower_table, label_col_index, min_gain)  # build tree
    # print_tree(tree, flower_features, label_col_index)

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
    construct_json(tree, flower_features, json_tree)
    write_json(json_tree)
