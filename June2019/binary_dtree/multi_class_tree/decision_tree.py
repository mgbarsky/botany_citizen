from math import log
import copy
import time
MISSINGCHAR = '?'
NUMERIC_COL_IDS = [5, 7, 9, 15, 19, 24, 25, 26, 33, 39, 40, 57, 60, 66, 77, 78, 79, 86, 89, 95, 103, 109, 115, 120, 121,
                   126, 127, 140, 143, 158, 172, 174, 175, 176, 179, 180, 182, 183, 185, 189, 190, 191, 193, 194, 195]

ATTRIBUTE_NAMES = None
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
    results = uniquecounts(rows, class_column)

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
            except ValueError:
                try:
                    attr_val_arr[val_index] = float(attr_val_arr[val_index].strip())
                except ValueError:
                    attr_val_arr[val_index] = attr_val_arr[val_index].strip()

    # When single val, put it into attr_val_arr
    else:
        try:
            attr_val_arr.append(int(str(raw_attr_val)))
        except ValueError:
            try:
                attr_val_arr.append(float(raw_attr_val))
            except ValueError:
                attr_val_arr.append(raw_attr_val.strip())

    return attr_val_arr


def is_num(val):
    try:
        float(val)
        return True
    except ValueError:
        return False


def convert_to_num(num):
    try:
        num = int(num)
        return num
    except ValueError:
        try:
            num = float(num)
            return num
        except ValueError:
            print('None-numeric! ', num)
            return None


# Take a list of symbols that can occur in the table and an value with interval
# Return the symbol and the interval number(s).
# If the interval is any, returned symbol as '^' and interval as [0, float("inf")]
def process_interval(interval_symbol_list, attr_val):
    if attr_val == 'any':
        return '^', [0, float("inf")]

    for symbol in interval_symbol_list:
        if symbol in attr_val:
            interval_values = list(filter(None, attr_val.split(symbol)))
            for val_index in range(len(interval_values)):
                interval_values[val_index] = convert_to_num(interval_values[val_index])
                if interval_values[val_index] is None:
                    print('None-numeric value in interval! ', attr_val)
                    exit(1)

            if symbol == ">=":
                return symbol, [interval_values[0], float("inf")]
            elif symbol == "<=":
                return symbol, [0, interval_values[0]]

            return symbol, interval_values

    print('Unknown symbol in the interval! ', attr_val)
    exit(1)


# Take the min value and max value of an interval
# Restore them using interval symbols
def restore_interval(min_val, max_val):
    if (min_val > max_val) or (min_val == float("inf") and max_val == float("inf")):
        print('Interval value error: [{}, {}]'.format(min_val, max_val))
        exit(1)
    elif min_val == 0 and max_val == float("inf"):
        return 'any'
    elif min_val == max_val:
        return str(max_val)
    elif max_val == float("inf"):
        return '>='+str(min_val)
    elif min_val == 0:
        return '<='+str(max_val)
    else:
        return '{}^{}'.format(min_val, max_val)


# Find the smallest change of last digit of num1/num2
def find_smallest_change(num1, num2):
    # When both numbers are int the smallest change will be 1
    if isinstance(num1, int) and isinstance(num2, int):
        return 1

    # Find the maximum number of digits if exist
    max_decimal_place = max(str(num1)[::-1].find('.'), str(num2)[::-1].find('.'))
    # When one number is int and another is float (max_decimal_place is -1), the smallest change is 1
    if max_decimal_place == -1:
        return 1

    # When at least one of the numbers is valid float, find the smallest change and return
    change = '1'
    for i in range(max_decimal_place - 1):
        change = '0' + change
    return float('0.' + change)


# Check if check if interval 1 overlaps with interval2
# Return the in-interval and out-interval
def separate_intervals(interval1, interval2):
    decrement = find_smallest_change(interval1[0], interval2[0])
    increment = find_smallest_change(interval2[1], interval1[1])

    # If interval1 is included in interval2
    if (interval2[0] <= interval1[0] <= interval2[1]) and (interval2[0] <= interval1[1] <= interval2[1]):
        # Return the 1 in-interval and nothing is out
        return interval1, None, None

    # If only the beginning part of interval1 is in interval2
    elif interval2[0] <= interval1[0] <= interval2[1]:
        # Return the 1 in-interval and 1 out-interval
        return [interval1[0], interval2[1]], \
               [round(interval2[1]+increment, 2), interval1[1]], None

    # If only the ending part of interval1 is in interval2
    elif interval2[0] <= interval1[1] <= interval2[1]:
        # Return the 1 in-interval and 1 out-interval
        return [interval2[0], interval1[1]], \
               [interval1[0], round(interval2[0]-decrement, 2)], None

    # If interval2 is completely in interval1
    elif interval1[0] <= interval2[0] <= interval1[1] and interval1[0] <= interval2[1] <= interval1[1]:
        # Return 1 in-interval and 2 out-intervals
        return interval2, [interval1[0], round(interval2[0] - decrement, 2)],\
               [round(interval2[1] + increment, 2), interval1[1]]

    # If two interval does not overlap at all
    else:
        # Return 1 out-interval and nothing is ins
        return None, interval1, None


def get_num_binary_set(rows, col_id, is_single_val, separator, interval_symbol_list, dividing_number=None,
                       dividing_symbol=None, dividing_interval_val=None):
    true_set = []
    false_set = []
    for r in rows:
        val_list = process_raw_val(r[0][col_id], is_single_val, separator)
        value_sets = [[], []]
        for val in val_list:
            # Put missing char to the false value set
            if val == MISSINGCHAR:
                value_sets[1].append(val)

            # If the row value at the column is a number
            elif is_num(val):
                # If divide the row by number
                if dividing_number is not None:
                    if val == dividing_number:
                        value_sets[0].append(str(val))
                    else:
                        value_sets[1].append(str(val))

                # If divide the row by interval
                else:
                    if dividing_interval_val[0] <= val <= dividing_interval_val[1]:
                        value_sets[0].append(str(val))
                    else:
                        value_sets[1].append(str(val))

            # If the row value is an interval
            else:
                val_symbol, val_interval = process_interval(interval_symbol_list, val)
                # If divide the row by a number
                if dividing_number is not None:
                    # If the number used to split is in the interval
                    if val_interval[0] <= dividing_number <= val_interval[1]:
                        value_sets[0].append(str(dividing_number))

                        decrement = find_smallest_change(val_interval[0], dividing_number)
                        increment = find_smallest_change(dividing_number, val_interval[1])

                        # print('\nInterval to be separated: {}, dividing_number:{}'.format(val_interval, dividing_number))

                        # Divide the interval into two excluding the number used to split
                        interval1 = restore_interval(val_interval[0], round(dividing_number-decrement, 2)) \
                            if dividing_number != val_interval[0] else None
                        interval2 = restore_interval(round(dividing_number+increment, 2), val_interval[1]) \
                            if dividing_number != val_interval[1] else None

                        # print('Separated interval1:{}, interval2:{}'.format(interval1, interval2))

                        # Append new intervals to false value set
                        if interval1 is not None:
                            value_sets[1].append(interval1)
                        if interval2 is not None:
                            value_sets[1].append(interval2)
                    # If the number used to split is not in the interval, append the interval to false value set
                    else:
                        value_sets[1].append(val)
                # If divide the row by an interval
                else:
                    true_interval, false_interval_1, false_interval_2 = \
                        separate_intervals(val_interval, dividing_interval_val)

                    if true_interval is not None:
                        value_sets[0].append(restore_interval(true_interval[0], true_interval[1]))
                    if false_interval_1 is not None:
                        value_sets[1].append(restore_interval(false_interval_1[0], false_interval_1[1]))
                    if false_interval_2 is not None:
                        value_sets[1].append(restore_interval(false_interval_2[0], false_interval_2[1]))

        if len(value_sets[0]) != 0:
            r_copy = copy.deepcopy(r)
            r_copy[0][col_id] = separator.join(value_sets[0])
            true_set.append(r_copy)
        if len(value_sets[1]) != 0:
            r_copy = copy.deepcopy(r)
            r_copy[0][col_id] = separator.join(value_sets[1])
            false_set.append(r_copy)

        # Debug for specific species
        # if r[1][0] == 'Desmodium rotundifolium' and ATTRIBUTE_NAMES[col_id] == 'Sepal length' and dividing_number == 2.5:
        #     print('Column id', col_id)
        #     print('Value sets:', value_sets)
        #     print('True set:', true_set)
        #     print('False set:', false_set)
        #     exit(10)

    return true_set, false_set


def divide_rows(rows, col_id, is_single_val, separator='||', interval_symbol_list=('^', '<=', '>=')):
    result = {}  # key is a distinct attr value in column col_id, value is a list of rows
    for row in rows:
        data = row[0]
        raw_attr_val = data[col_id]
        if raw_attr_val == '?' or raw_attr_val in result:
            continue

        attr_val_arr = process_raw_val(raw_attr_val, is_single_val, separator)
        # Iterate the or-split list (or a list with a single val)
        for attr_val in attr_val_arr:
            # Not using missing char or repeated value to split
            if attr_val == MISSINGCHAR or attr_val in result:
                continue

            result[attr_val] = []
            true_set = []
            false_set = []
            # Numeric values
            if col_id in NUMERIC_COL_IDS:
                # If attribute value to split on is a number
                if is_num(attr_val):
                    true_set, false_set = get_num_binary_set(rows, col_id, is_single_val, separator,
                                                             interval_symbol_list, dividing_number=attr_val)
                # If attribute value to split on is an interval
                else:
                    symbol, interval_val = process_interval(interval_symbol_list, attr_val)
                    true_set, false_set = get_num_binary_set(rows, col_id, is_single_val, separator, interval_symbol_list,
                                                             dividing_symbol=symbol, dividing_interval_val=interval_val)

            # Categorical value
            else:
                for r in rows:
                    val_arr = process_raw_val(r[0][col_id], is_single_val, separator)
                    # Divide the rows into two sets
                    if attr_val in val_arr:
                        r_copy = copy.deepcopy(r)
                        r_copy[0][col_id] = attr_val
                        true_set.append(r_copy)

                        # Divide the other non-belonging or separated values into the false set
                        if len(val_arr) > 1:
                            val_arr.remove(attr_val)
                            r_copy = copy.deepcopy(r)
                            r_copy[0][col_id] = separator.join(val_arr)
                            false_set.append(r_copy)

                    # For single-valued false set
                    else:
                        r_copy = copy.deepcopy(r)
                        false_set.append(r_copy)

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
def build_tree(rows, flower_features, class_label_col, min_gain, col_not_used, is_single_val=False
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
        # print("len rows", len(rows))
        # if col_id in NUMERIC_COL_IDS:
        #     continue

        # print('\nAttribute to split:', flower_features[col_id])
        sets = divide_rows(rows, col_id, is_single_val)
        # elapsed_time = time.time() - start_time
        # print(elapsed_time, 'Seconds')
        # print('Number of sets:', len(sets))

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

        return build_tree(decision_node.results, flower_features, decision_node.class_id, min_gain, col_not_used,
                          is_single_val=False,
                          scoref=entropy, total_score_func=total_entropy_of_split)

    decision_node.results = []  # Empty the result list when it's not a leaf node
    decision_node.question = flower_features[best_column] + '({})'.format(best_val_key)

    for col_index in range(len(col_not_used)):
        if best_column == col_not_used[col_index]:
            del col_not_used[col_index]
            break

    # Get the best row sets with binary split
    best_sets = divide_rows(rows, best_column, is_single_val)[best_val_key]

    print('Length of true set: {}, Length of false set: {}'.format(len(best_sets[0]), len(best_sets[1])))
    # Attach the true branch and false branch to the current node
    decision_node.tb = \
        build_tree(best_sets[0], flower_features,  decision_node.class_id, min_gain, col_not_used, is_single_val,
                   scoref, total_score_func)
    decision_node.fb = \
        build_tree(best_sets[1], flower_features, decision_node.class_id, min_gain, col_not_used, is_single_val,
                   scoref, total_score_func)

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
