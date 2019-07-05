from math import log
MISSINGCHAR = '?'


class DecisionNode:
  def __init__(self, attr_col=-1,
               question=None, answer_to_parent=None, children=None, results=None):
    self.attr_col = attr_col  # col id of the attribute we split on
    self.answer_to_parent = answer_to_parent
    self.children = children  # list of decision nodes
    self.results = results  # list of final class labels - in case it is a leaf node


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
def entropy(rows,class_column):
    log2 = lambda x:log(x)/log(2)
    results=uniquecounts(rows,class_column)
    # Now calculate the entropy
    ent = 0.0
    for r in results.keys():
        p = float(results[r])/len(rows)  # probability at the level
        ent = ent-p*log2(p)
    return ent


def divide_rows(rows, col_id):
    result = {}  # key is a distinct attr value in column col_id, value is a list of rows
    numeric_bool = False  # check if current col is numeric

    for row in rows:
        data = row[0]
        attr_val = data[col_id]
        if attr_val not in result and attr_val != MISSINGCHAR:
            result[attr_val] = []

        # Numerical values
        if isinstance(attr_val, int) or isinstance(attr_val, float):
            if not result[attr_val]:
                numeric_bool = True
                # the result dic keys will be all possible numerical values in a col,
                # and the value is a list of binary split rows
                sub_set = {'>=' + str(attr_val): [],
                           '<' + str(attr_val): []}
                for r in rows:
                    # Skip the missing char
                    if r[0][col_id] == MISSINGCHAR:
                        continue
                    elif r[0][col_id] >= attr_val:
                        sub_set['>=' + str(attr_val)].append(r)
                    else:
                        sub_set['<' + str(attr_val)].append(r)
                result[attr_val] = sub_set

        # Categorical values
        elif attr_val != MISSINGCHAR:
            result[attr_val].append(row)

    # Add missing char row to all split rows
    for row in rows:
        data = row[0]
        attr_val = data[col_id]
        if attr_val == MISSINGCHAR:
            for value in result.keys():
                if isinstance(value, int) or isinstance(value, float):
                    result[value]['>=' + str(value)].append(row)
                    result[value]['<' + str(value)].append(row)
                else:
                    result[value].append(row)

    return result, numeric_bool


def info_ratio(row_sets, class_label_col, scoref=entropy):
    log2 = lambda x: log(x) / log(2)

    total_row_len = 0
    for val_list in row_sets.values():
        total_row_len += len(val_list)

    intrinsic_info = 0
    for val_list in row_sets.values():
        p = len(val_list) / total_row_len
        intrinsic_info -= p*log2(p)

    if intrinsic_info == 0:
        return None

    total_ent = 0
    for val_list in row_sets.values():
        w = len(val_list) / total_row_len
        ent = scoref(val_list, class_label_col)
        total_ent += w * ent
    return total_ent/intrinsic_info


# Divides a set on a specific column. Can handle numeric
# or nominal values
def build_tree(answer_to_parent, rows, class_label_col, scoref=entropy, total_score_func=info_ratio):
    decision_node = DecisionNode()
    decision_node.results = rows
    decision_node.answer_to_parent = answer_to_parent

    if len(rows) == 0: return decision_node  # tbd
    current_score = total_score_func({"1": rows}, class_label_col)
    if current_score is None:
        return decision_node
    parent_score = current_score

    if current_score == 0:
        return decision_node  # tbd

    # Set up some variables to track the best split criteria
    best_column = None
    best_num_val = None
    score = None
    column_count = len(rows[0][0])

    # Find the best col
    for col_id in range(column_count):
        sets, numeric_bool = divide_rows(rows, col_id)
        current_num_val = None
        # Score for numeric values
        if numeric_bool:
            min_num_score = None
            # find the current numeric val
            for val_key, row_sets in sets.items():
                cur_score = total_score_func(row_sets, class_label_col, scoref)
                if cur_score is None:
                    continue
                if current_num_val is None or cur_score < min_num_score:
                    min_num_score = total_score_func(row_sets, class_label_col, scoref)
                    current_num_val = val_key
            score = min_num_score

        # Score for categorical value
        else:
            score = total_score_func(sets, class_label_col, scoref)
            # print(score)

        if score is not None and score < current_score:
            current_score = score
            best_column = col_id
            best_num_val = current_num_val

    gain = parent_score - current_score

    if gain < 0.001:  # to set up min gain
        return decision_node  # tbd
    decision_node.results = []
    decision_node.attr_col = best_column
    decision_node.children = []
    row_sets, numeric_bool = divide_rows(rows, best_column)

    # When the best col is numeric
    if numeric_bool:
        row_sets = row_sets[best_num_val]

    # When the row_sets are empty
    if not row_sets:
        decision_node.results = rows
        return decision_node

    for attr_val, row_set in row_sets.items():
        child = build_tree(attr_val, row_set, class_label_col, scoref, total_score_func)
        decision_node.children.append(child)

    return decision_node


def print_tree(current_node, questions_list, label_col_index, indent=''):
    node_repr = indent + "parent_answ={} ".format(current_node.answer_to_parent)

    if current_node.results and len(current_node.results) > 0:
        node_repr += str(uniquecounts(current_node.results,
                                      len(current_node.results[0][1])+label_col_index))
        print(node_repr)
        return

    node_repr += "q={} ".format(questions_list[current_node.attr_col])
    print(node_repr)
    indent += '  '
    for child in current_node.children:
        print_tree(child, questions_list, label_col_index, indent)


# Construct json based on the tree
def construct_json(current_node, questions_list, label_col_index, json_tree):
    name = '(A:' + str(current_node.answer_to_parent) + ').  '
    if current_node.results and len(current_node.results) > 0:
        for label in uniquecounts(current_node.results, len(current_node.results[0][1])+label_col_index).keys():
            name += str(label) + '\n'
        # Leaf
        json_tree["name"] = name
        return json_tree

    name += questions_list[current_node.attr_col]
    if 'None' in name:
        name = questions_list[current_node.attr_col]

    # Question
    json_tree["name"] = name
    json_tree["children"] = []

    count = 0
    for child in current_node.children:
        json_tree["children"].append({})
        construct_json(child, questions_list, label_col_index, json_tree["children"][count])
        count += 1
