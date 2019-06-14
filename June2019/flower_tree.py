from decision_tree import *
import json
import itertools

NUM_COLS = 0  # 11 or 23
MAX_DEPTH = 20


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


def flatten_alt_values(rows, delimiter=' or '):  # deliminator is used for splitting multiple values at a col
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
            print ("Too many permutations for Row",r)

    return new_rows

if __name__ == "__main__":
    # print("Reading in file...")
    # flower_table: list of list of feature rows, flower_features: list of attributes
    flower_table, flower_features = read_data("d_flower_data_full.tsv")
    delimited_flower_table = flatten_alt_values(flower_table)
    print("{} observations, {} features".format(len(delimited_flower_table), NUM_COLS))
    # flower_features = ["Q1", "Q2", "Q3", "Q4", "Q5"]
    # delimited_flower_table = [
    #     [[3, "a", 4, "a", "x"],["class1", "top class1"]],
    #     [[5, "b", 4, "b", "x"], ["class1", "top class1"]],
    #     [[7, "b", 4, "c", "y"], ["class1", "top class1"]],
    #     [[3, "a", 4, "a", "x"], ["class2", "top class2"]],
    #     [[5, "a", 4, "b", "x"], ["class2", "top class2"]],
    #     [[7, "b", 1, "c", "y"], ["class2", "top class2"]],
    #     [[3, "b", 1, "a", "x"], ["class2", "top class2"]],
    #     [[5, "b", 1, "b", "z"], ["class2", "top class2"]],
    #     [[7, "a", 1, "c", "z"], ["class2", "top class2"]],
    #     [[7, "a", 1, "a", "z"], ["class2", "top class2"]],
    # ]
    print("Building tree...")

    tree = build_tree(None, delimited_flower_table, len(delimited_flower_table[0][1]) -1)  # build tree

    print_tree(tree, flower_features)
