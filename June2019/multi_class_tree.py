from decision_tree import *
import json
import itertools

NUM_COLS = 0  # 11 or 23
LABEL_COL_INDEX = -4  # the index of hierarchical label to classify


def read_data(filename):
    global NUM_COLS
    input_f = open(filename, encoding="latin1")
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
                print("Error on row",row_id, "Not enough columns!")
                exit(1)
            for i in range(len(arr)):
                try:
                    arr[i] = int(arr[i])
                except ValueError:
                    pass

            row = arr[0:NUM_COLS]
            labels = arr[NUM_COLS:]

            rows.append([row]+[labels])

            if len(labels) != 4:
                print("Error on row", row_id)
                print("Not all labels specified")
                exit(1)
    input_f.close()
    return rows, feature_dict


def flatten_alt_values(rows):  # deliminator is used for splitting multiple values at a col
    """The function takes all rows (with repeated values in certain cols) in a table
    and output new_rows with only one value at each col"""

    new_rows = []  # new_rows with each row having one value at a col

    r = 0
    for row in rows:
        r += 1
        try:
            data_cols = []
            perm_input = []

            has_alt = False
            for col_id in range(len(row[0])):
                if ' or ' in str(row[0][col_id]):
                    has_alt = True
                    v = row[0][col_id]
                    alt_values = v.split(' or ')
                    for k in range(len(alt_values)):
                        try:
                            alt_values[k] = int(alt_values[k])
                        except:
                            pass
                    perm_input.append(alt_values)
                    data_cols.append(col_id)

            if has_alt:
                # using itertools.product()
                # to compute all possible permutations
                permuted = list(itertools.product(*perm_input))

                labels = row[1]
                for new_vals in permuted:
                    new_row_data = row[0][:]
                    for i in range(len(new_vals)):
                        new_row_data[data_cols[i]] = new_vals[i]

                    new_row = [new_row_data] + [labels[:]]
                    new_rows.append(new_row)
            else:
                new_rows.append(row[:])
        except MemoryError:
            print("Too many permutations for Row", r)

    return new_rows


# Find number of labels on leaves and branch depths, which are put into leaf_label_count_arr, depth_arr respectively
def leaf_label_and_depth_count(current_node, leaf_label_count_arr, depth_arr, current_depth=0):
    # Leaf
    if current_node.results and len(current_node.results) > 0:
        leaf_label_count_arr.append(len(uniquecounts(current_node.results,
                                                     len(current_node.results[0][1]) + LABEL_COL_INDEX).keys()))
        return

    # Compute the depth of each sub-branch
    current_depth += 1
    depth_arr.append(current_depth)

    for child in current_node.children:
        leaf_label_and_depth_count(child, leaf_label_count_arr, depth_arr, current_depth)


def get_max_and_ave(leaf_label_count_arr):
    return max(leaf_label_count_arr), sum(leaf_label_count_arr)/len(leaf_label_count_arr)


def write_json(json_tree):
    with open('test_tree.json', 'w') as outfile:
        json.dump(json_tree, outfile)


if __name__ == "__main__":
    print("Reading in file...")
    # flower_table: list of list of feature rows, flower_features: list of attributes
    flower_table, flower_features = read_data("d_flower_data_full.tsv")
    delimited_flower_table = flatten_alt_values(flower_table)
    print("{} observations, {} features".format(len(delimited_flower_table), NUM_COLS))
    # flower_features = ["Q1", "Q2", "Q3", "Q4", "Q5"]
    # delimited_flower_table = [
    #     [['?', "?", 1, "a", "x"], ["class1", "top class3"]],
    #     [[4, "b", 1, "b", "x"], ["class1", "top class4"]],
    #     [[3, "b", 3, "c", "y"], ["class1", "top class3"]],
    #     [[20, "a", 20, "a", "x"], ["class2", "top class2"]],
    #     [['?', "a", 5, "?", "x"], ["class2", "top class2"]],
    #     [[8, "b", 2, "c", "?"], ["class2", "top class4"]],
    #     [[10, "b", 3, "c", "x"], ["class2", "top class2"]],
    #     [[10, "b", 6, "b", "z"], ["class2", "top class2"]],
    #     [[15, "a", 10, "d", "z"], ["class2", "top class5"]],
    #     [['?', "a", 12, "d", "?"], ["class2", "top class5"]],
    # ]
    print("Building tree...")
    tree = build_tree(None, delimited_flower_table, len(delimited_flower_table[0][1])+LABEL_COL_INDEX)  # build tree
    print_tree(tree, flower_features, LABEL_COL_INDEX)

    leaf_label_count_arr = []  # a list of number of leaf labels
    depth_arr = []  # a list of branch depths

    leaf_label_and_depth_count(tree, leaf_label_count_arr, depth_arr)

    # Get max number of labels on leaves and average number of labels
    max_leaf_lab_num, ave_leaf_lab_num = get_max_and_ave(leaf_label_count_arr)
    # Get max depth and average depth of the tree
    max_dep, ave_depth = get_max_and_ave(depth_arr)

    print("The max depth of the tree is: ", max_dep)
    print("The average depth of the tree is: ", ave_depth)
    print("The max number of labels is: ", max_leaf_lab_num)
    print("The average number of classes per leaf is: ", ave_leaf_lab_num)

    json_tree = {}
    construct_json(tree, flower_features, LABEL_COL_INDEX, json_tree)
    write_json(json_tree)
