from math import log
MISSINGCHAR = '?'
NUMERIC_COL_IDS = [5, 7, 9, 15, 19, 24, 25, 26, 33, 39, 40, 57, 60, 66, 77, 78, 79, 86, 89, 95, 103, 109, 115, 120, 121,
                  126, 127, 140, 143, 158, 172, 174, 175, 176, 179, 180, 182, 183, 185, 189, 190, 191, 193, 194, 195]


class DecisionNode:
    def __init__(self, question=None, results=None, tb=None, fb=None):
        self.question = question  # the concatenation between the attribute and the value to split on
        self.results = results  # list of final class labels - in case it is a leaf node
        self.tb = tb  # True branch (yes answer)
        self.fb = fb  # False branch (no answer)
        self.class_id = 0


# Create counts of possible class labels in the same group of rows
def uniquecounts(rows, class_col_id):
    results = {}
    for row in rows:
        # The result is in the column specified by scorevar
        r = row[1][class_col_id]
        if r not in results: results[r] = 0
        results[r] += 1
    return results  # An array of counts per each unique val in the labels column


# Entropy is the sum of p(x)log(p(x)) across all
# the different labels for the records in the same group
def entropy(rows, class_column):
    log2 = lambda x: 0 if x == 0 else log(x)/log(2)
    results=uniquecounts(rows,class_column)
    # Now calculate the entropy
    ent = 0.0
    for r in results.keys():
        p = float(results[r])/len(rows)  # probability at the level
        ent = ent-p*log2(p)
    return ent


# Take a value (either single or separated by ' or ') and return a list that contains value(s)
def process_raw_val(raw_attr_val, is_single_val, separator):
    attr_val_arr = []  # List contains the correct values
    # When or in value, split and put into attr_val_arr
    if is_single_val is False and separator in str(raw_attr_val):
        attr_val_arr = raw_attr_val.split(separator)
        for val_index in range(len(attr_val_arr)):
            try:
                attr_val_arr[val_index] = int(attr_val_arr[val_index].strip())
            except:
                attr_val_arr[val_index] = attr_val_arr[val_index].strip()

    # When single val, put it into attr_val_arr
    else:
        try:
            attr_val_arr.append(int(raw_attr_val.strip()))
        except:
            attr_val_arr.append(raw_attr_val.strip())

    return attr_val_arr


def divide_rows(rows, col_id, is_single_val, separator='||'):
    result = {}  # key is a distinct attr value in column col_id, value is a list of rows
    for row in rows:
        data = row[0]
        raw_attr_val = data[col_id]
        attr_val_arr = process_raw_val(raw_attr_val, is_single_val, separator)
        # Iterate the or-split list (or a list with a single val)
        for attr_val in attr_val_arr:
            # Not using missing char or repeated value to split
            if attr_val == MISSINGCHAR or attr_val in result:
                continue

            result[attr_val] = []
            true_set = []
            false_set = []

            # Categorical values
            for r in rows:
                val_arr = process_raw_val(r[0][col_id], is_single_val, separator)
                # Divide the rows into two sets
                if attr_val in val_arr:
                    r[0][col_id] = attr_val
                    true_set.append(r)
                    # Divide the other non-belonging or separated values into the false set
                    if len(val_arr) > 1:
                        val_arr.remove(attr_val)
                        r[0][col_id] = separator.join(val_arr)
                        false_set.append(r)

                # For single-valued false set
                else:
                    false_set.append(r)

            result[attr_val].append(true_set)
            result[attr_val].append(false_set)

    return result


def total_entropy_of_split(row_sets, class_label_col, scoref=entropy):
    total_row_len = 0
    for val_list in row_sets:
        total_row_len += len(val_list)

    total_ent = 0
    for val_list in row_sets:
        w = len(val_list) / total_row_len
        ent = scoref(val_list, class_label_col)
        total_ent += w * ent

    return total_ent


def intrinsic_info(row_sets):
    log2 = lambda x: log(x) / log(2)

    total_row_len = 0
    for val_list in row_sets:
        total_row_len += len(val_list)

    intrinsic_val = 0
    for val_list in row_sets:
        if not val_list: continue
        p = len(val_list) / total_row_len
        intrinsic_val -= p*log2(p)

    if intrinsic_val == 0:  # If there is only a single branch; this will cause the gain ratio to be 0
        return float("inf")

    return intrinsic_val


# Divides a set on a specific column. Can handle numeric
# or nominal values
def build_tree(rows, flower_features, class_label_col, min_gain, is_single_val=False
               , scoref=entropy, total_score_func=total_entropy_of_split):
    decision_node = DecisionNode()
    decision_node.results = rows
    decision_node.class_id = class_label_col

    # Set up cur and parent score to calculate gain later
    current_score = total_score_func([rows], class_label_col)
    parent_score = current_score

    # Set up some variables to track the best split criteria
    best_column = None
    best_val_key = None
    column_count = len(rows[0][0])

    # Find the best col
    for col_id in range(column_count):
        # Skip the numeric columns for now
        if col_id in NUMERIC_COL_IDS:
            continue
        # print("len rows", len(rows))
        sets = divide_rows(rows, col_id, is_single_val)
        # print(len(sets.values()))
        current_val = None
        score = None
        for val_key, row_sets in sets.items():
            sets_score = total_score_func(row_sets, class_label_col)
            if score is None or sets_score < score:
                score = sets_score
                current_val = val_key

        # Total entropy
        if score is not None and score < current_score:
            current_score = score
            best_column = col_id
            best_val_key = current_val

    gain = parent_score - current_score

    if gain < min_gain:  # to set up min gain
        # for row in rows:
        #     print(row)
        # print("parent_score=", parent_score)
        # print("current_score=", current_score)
        # print("best_col=", best_column)
        # print("gain=", gain)

        if decision_node.class_id > 0: # when it's not the lowest level
            decision_node.class_id -= 1
        else:
            return decision_node

        return build_tree(decision_node.results, flower_features, decision_node.class_id, min_gain,
                          is_single_val=False,
                          scoref=entropy, total_score_func=total_entropy_of_split)

    decision_node.results = []  # Empty the result list when it's not a leaf node
    decision_node.question = flower_features[best_column] + '({})'.format(best_val_key)

    # Get the best row sets with binary split
    best_sets = divide_rows(rows, best_column, is_single_val)[best_val_key]

    # Attach the true branch and false branch to the current node
    decision_node.tb = \
        build_tree(best_sets[0], flower_features,  decision_node.class_id, min_gain, is_single_val, scoref, total_score_func)
    decision_node.fb = \
        build_tree(best_sets[1], flower_features, decision_node.class_id, min_gain, is_single_val, scoref, total_score_func)

    return decision_node


def print_tree(current_node, branch_name='', indent=''):
    node_repr = indent

    if current_node.results and len(current_node.results) > 0:
        node_repr += branch_name + str(uniquecounts(current_node.results, current_node.class_id))
        print(node_repr)
        return

    node_repr += branch_name + "q={} ".format(current_node.question)
    print(node_repr)
    indent += '  '

    print_tree(current_node.tb, 'T-> ', indent)
    print_tree(current_node.fb, 'F-> ', indent)


# Construct json based on the tree
def construct_json(current_node, json_tree, branch_name=''):
    name = "(A: {} ).  ".format(branch_name)
    if current_node.results and len(current_node.results) > 0:
        for label in uniquecounts(current_node.results, current_node.class_id).items():
            name = name + str(current_node.class_id) + ':' + str(label) + '\n'
        # Leaf
        json_tree["name"] = name
        return json_tree

    name += current_node.question
    if 'None' in name:
        name = current_node.question

    # Question
    json_tree["name"] = name
    json_tree["children"] = [{}, {}]

    construct_json(current_node.tb,  json_tree["children"][0], 'YES')
    construct_json(current_node.fb, json_tree["children"][1], 'NO')
