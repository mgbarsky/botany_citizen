from math import log
MISSINGCHAR = '?'
# compare genus

class DecisionNode:
  def __init__(self, attr_col=-1,
               question=None, answer_to_parent=None, children=None, results=None):
    self.attr_col = attr_col  # col id of the attribute we split on
    self.answer_to_parent = answer_to_parent
    self.children = children  # list of decision nodes
    self.results = results  # list of final class labels - in case it is a leaf node
    self.class_id = 0


# Sum of squared distances from the mean
def vector_variance(rows, weights):
    # Only happens for numeric splits which have 0 entries in one region, variance reduction will be 0
    if len(rows) == 0:
        return 0

    # Calculate mean vector
    mean_vector = [0]*len(rows[0][1])  # Initialize mean vector to 0
    for row in rows:
        vector = row[1]
        for i in range(len(vector)):
            mean_vector[i] += vector[i]

    for i in range(len(mean_vector)):
        mean_vector[i] /= len(rows)  # Average

    sum_squared = 0
    for row in rows:
        vector = row[1]
        for i in range(len(vector)):
            # Weight squared differences smaller when deeper in the tree
            sum_squared += weights[i]*pow(vector[i] - mean_vector[i], 2)

    return sum_squared/len(rows)


def vector_variance_of_split(row_sets, weights, scoref=vector_variance):
    total_row_len = 0
    for val_list in row_sets.values():
        total_row_len += len(val_list)

    total_variance = 0
    for k, val_list in row_sets.items():
        w = len(val_list) / total_row_len
        var = scoref(val_list, weights)
        total_variance += w * var

    return total_variance


# Take a value (either single or separated by ' or ') and return a list that contains value(s)
def process_raw_val(raw_attr_val, is_single_val, separator):
    attr_val_arr = []  # List contains the correct values
    # When or in value, split and put into attr_val_arr
    if is_single_val is False and separator in str(raw_attr_val):
        attr_val_arr = raw_attr_val.split(separator)
        for val_index in range(len(attr_val_arr)):
            try:
                attr_val_arr[val_index] = int(attr_val_arr[val_index])
            except:
                pass

    # When single val, put it into attr_val_arr
    else:
        try:
            attr_val_arr.append(int(raw_attr_val))
        except:
            attr_val_arr.append(raw_attr_val)

    return attr_val_arr


def divide_rows(rows, col_id, is_single_val, separator=' or '):
    result = {}  # key is a distinct attr value in column col_id, value is a list of rows
    numeric_bool = False  # check if current col is numeric

    for row in rows:
        data = row[0]
        raw_attr_val = data[col_id]
        attr_val_arr = process_raw_val(raw_attr_val, is_single_val, separator)
        for attr_val in attr_val_arr:
            if attr_val not in result and attr_val != MISSINGCHAR:
                result[attr_val] = []

            # Numerical values
            if isinstance(attr_val, int) or isinstance(attr_val, float):
                if not result[attr_val]:
                    numeric_bool = True
                    sub_set = {'>=' + str(attr_val): [],
                               '<' + str(attr_val): []}
                    for r in rows:
                        num_val_arr = process_raw_val(r[0][col_id], is_single_val, separator)
                        sets = [[], []]
                        for num_val in num_val_arr:
                            # Skip the missing char
                            if num_val == MISSINGCHAR:
                                continue
                            # Divide into 2 sets
                            # Go into sets[0] if value is greater than splitting value
                            elif num_val >= attr_val:
                                sets[0].append(str(num_val))
                            else:
                                sets[1].append(str(num_val))

                        # Modify r so that its column only contains the proper values, also in "or" format
                        # If it's singular then it must be an integer
                        # Then append the new row to the appropriate key in sub_set
                        if len(sets[0]) != 0:
                            r[0][col_id] = separator.join(sets[0]) if is_single_val is False \
                                                                   and len(sets[0]) > 1 else int(sets[0][0])
                            sub_set['>=' + str(attr_val)].append(list(r))
                        if len(sets[1]) != 0:
                            r[0][col_id] = separator.join(sets[1]) if is_single_val is False \
                                                                   and len(sets[1]) > 1 else int(sets[1][0])
                            sub_set['<' + str(attr_val)].append(list(r))
                    # the result dic keys will be all possible numerical values in a col,
                    # and the value is a list of binary split rows
                    result[attr_val] = sub_set

            # Categorical values
            elif attr_val != MISSINGCHAR:
                row[0][col_id] = attr_val
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


# Divides a set on a specific column. Can handle numeric
# or nominal values
def build_tree(answer_to_parent, rows, weights, is_single_val=False
               ,scoref=vector_variance, total_score_func=vector_variance_of_split):
    decision_node = DecisionNode()
    decision_node.results = rows
    decision_node.answer_to_parent = answer_to_parent
    if len(rows) == 0:
        return decision_node  # tbd

    current_score = scoref(rows, weights)
    parent_score = current_score

    if parent_score == 0:
        return decision_node

    # Set up some variables to track the best split criteria
    best_column = None
    best_num_val = None
    column_count = len(rows[0][0])

    # Find the best col
    for col_id in range(column_count):
        sets, numeric_bool = divide_rows(rows, col_id, is_single_val)
        current_num_val = None
        # Score for numeric values
        if numeric_bool:
            # Find the current numeric val
            min_num_score = None
            for val_key, row_sets in sets.items():
                cur_num_score = total_score_func(row_sets, weights)
                if min_num_score is None or cur_num_score < min_num_score:
                    min_num_score = cur_num_score
                    current_num_val = val_key
            score = min_num_score

        # Score for categorical value
        else:
            score = total_score_func(sets, weights)

        # total entropy
        if score < current_score:
            current_score = score
            best_column = col_id
            best_num_val = current_num_val

    gain = parent_score - current_score
    if gain == 0:  # to set up min gain
        return decision_node

    decision_node.results = []
    decision_node.attr_col = best_column
    decision_node.children = []
    row_sets, numeric_bool = divide_rows(rows, best_column, is_single_val)

    # When the best col is numeric
    if numeric_bool:
        row_sets = row_sets[best_num_val]

    # When the row_sets are empty
    if not row_sets:
        decision_node.results = rows
        return decision_node

    for attr_val, row_set in row_sets.items():
        child = build_tree(attr_val, row_set, weights,
                           is_single_val=is_single_val, scoref=scoref, total_score_func=total_score_func)
        decision_node.children.append(child)

    return decision_node


# Average the vectors at a leaf node and get a score for each label (only include nonzero ones)
# Return a list of tuples of (label name, score)
def vectors_to_labels(rows, label_list):
    label_scores = []
    average = [0]*len(label_list)  # Initialize average to zero vector

    for row in rows:
        vector = row[1]
        for i in range(len(label_list)):
            average[i] += vector[i]

    for i in range(len(label_list)):
        average[i] /= len(rows)
        if average[i] != 0:
            label_scores.append((label_list[i], average[i]))  # If the score is nonzero, append (label name, score)

    return label_scores


# Construct json based on the tree
def construct_json(current_node, questions_list, label_list, json_tree):
    name = '(A:' + str(current_node.answer_to_parent) + ').  '
    if current_node.results and len(current_node.results) > 0:
        # Leaf
        for tup in vectors_to_labels(current_node.results, label_list):
            name += "\n{}: {}".format(tup[0], round(tup[1], 2))

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
        construct_json(child, questions_list, label_list, json_tree["children"][count])
        count += 1
