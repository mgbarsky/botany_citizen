var MISSINGCHAR = '-1';
var NUMERIC_COL_IDS = [
  5,
  7,
  9,
  15,
  19,
  24,
  25,
  26,
  33,
  39,
  40,
  57,
  60,
  66,
  77,
  78,
  79,
  86,
  89,
  95,
  103,
  109,
  115,
  120,
  121,
  126,
  127,
  140,
  143,
  158,
  172,
  174,
  175,
  176,
  179,
  180,
  182,
  183,
  185,
  189,
  190,
  191,
  193,
  194,
  195
];
var decision_arrays = [];

// Create counts of possible class labels in the same group of rows
function uniquecounts(rows, class_col_id) {
  var results = {};
  for (row of rows) {
    // The result is in the column specified by scorevar
    var r = row[1][class_col_id];
    if (!Object.keys(results).includes(r)) {
      results[r] = 0;
    }
    results[r] += 1;
  }
  return results; // An array of counts per each unique val in the labels column
}

function log2(x) {
  if (x == 0) {
    return 0;
  } else {
    return Math.log(x) / Math.log(2);
  }
}

function entropy(rows, class_column) {
  var results = uniquecounts(rows, class_column);
  // Now calculate the entropy
  var ent = 0.0;
  for (var r in results) {
    var p = parseFloat(results[r]) / rows.length; // probability at the level
    ent = ent - p * log2(p);
  }
  return ent;
}

// Take a value (either single or separated by ' or ') and return a list that contains value(s)
function process_raw_val(raw_attr_val, separator) {
  var attr_val_arr = []; // List contains the correct values
  // When or in value, split and put into attr_val_arr
  if (String(raw_attr_val).includes(separator)) {
    attr_val_arr = raw_attr_val.split(separator);

    for (var val_index = 0; val_index < attr_val_arr.length; val_index++) {
      var val = parseFloat(attr_val_arr[val_index]);

      if (!isNaN(val)) {
        attr_val_arr[val_index] = val;
      }
    }
  }
  // When single val, put it into attr_val_arr
  else {
    var val = parseFloat(raw_attr_val);
    if (!isNaN(val)) {
      attr_val_arr.push(val);
    }
  }
  return attr_val_arr;
}

function is_num(val) {
  return !isNaN(val);
}

function round(num, decimal_places) {
  if (Number.isInteger(num)) return num;
  else return num.toFixed(decimal_places);
}

function convert_to_num(val) {
  var num = parseFloat(val);
  if (is_num(num)) {
    return num;
  } else {
    console.log('Parse none-numeric value error', val);
    return null;
  }
}

// Return a new array without non-number or null
function remove_nonetype(array) {
  var new_arr = [];
  for (ele of array) {
    if (ele != null && !isNaN(ele) && ele != '') {
      new_arr.push(ele);
    }
  }
  return new_arr;
}

// Take a list of symbols that can occur in the table and an value with interval
// Return the symbol and the interval number(s).
// If the interval is any, returned symbol as '^' and interval as [0, Infinity]
function process_interval(interval_symbol_list, attr_val) {
  if (attr_val == 'any') {
    return [0, Infinity];
  }

  for (symbol of interval_symbol_list) {
    if (attr_val.includes(symbol)) {
      var interval_values = remove_nonetype(attr_val.split(symbol));
      for (var val_index = 0; val_index < interval_values.length; val_index++) {
        interval_values[val_index] = convert_to_num(interval_values[val_index]);
        if (interval_values[val_index] == null) {
          console.log('None-numeric value in interval! ', attr_val);
        }
      }
      if (symbol == '>=') {
        return [interval_values[0], Infinity];
      } else if (symbol == '<=') {
        return [0, interval_values[0]];
      }

      return interval_values;
    }
  }
  console.log('Unknown symbol in the interval! ', attr_val);
}

// Take the min value and max value of an interval
// Restore them using interval symbols
function restore_interval(min_val, max_val) {
  if (min_val > max_val || (min_val == Infinity && max_val == Infinity)) {
    console.log('Interval value error:', [min_val, max_val]);
  } else if (min_val == 0 && max_val == Infinity) {
    return 'any';
  } else if (min_val == max_val) {
    return String(max_val);
  } else if (max_val == Infinity) {
    return '>=' + String(min_val);
  } else if (min_val == 0) {
    return '<=' + String(max_val);
  } else {
    return String(min_val) + '^' + String(max_val);
  }
}

Number.prototype.countDecimals = function() {
  if (Math.floor(this.valueOf()) === this.valueOf()) return 0;
  return this.toString().split('.')[1].length || 0;
};

// Find the smallest change of last digit of num1/num2
function find_smallest_change(num1, num2) {
  // When both numbers are int the smallest change will be 1
  if (Number.isInteger(num1) && Number.isInteger(num2)) {
    return 1;
  }
  // Find the maximum number of digits if exist
  max_decimal_place = Math.max(num1.countDecimals(), num2.countDecimals());
  // When one number is int and another is float, the smallest change is 1
  if (max_decimal_place == 0) {
    return 1;
  }

  // When at least one of the numbers is valid float, find the smallest change and return
  var change = '1';
  for (var i = 0; i < max_decimal_place - 1; i++) {
    change = '0' + change;
  }

  return parseFloat('0.' + change);
}

// Check if check if interval 1 overlaps with interval2
// Return the in-interval and out-interval
function separate_intervals(interval1, interval2) {
  var decrement = find_smallest_change(interval1[0], interval2[0]);
  var increment = find_smallest_change(interval2[1], interval1[1]);

  // If interval1 is included in interval2
  if (
    interval2[0] <= interval1[0] &&
    interval1[0] <= interval2[1] &&
    (interval2[0] <= interval1[1] && interval1[1] <= interval2[1])
  ) {
    // Return the 1 in-interval and nothing is out
    return [interval1, null, null];
  }
  // If only the beginning part of interval1 is in interval2
  else if (interval2[0] <= interval1[0] && interval1[0] <= interval2[1]) {
    // Return the 1 in-interval and 1 out-interval
    return [[interval1[0], interval2[1]], [round(interval2[1] + increment, 2), interval1[1]], null];
  }
  // If only the ending part of interval1 is in interval2
  else if (interval2[0] <= interval1[1] && interval1[1] <= interval2[1]) {
    // Return the 1 in-interval and 1 out-interval
    return [[interval2[0], interval1[1]], [interval1[0], round(interval2[0] - decrement, 2)], null];
  }
  // If interval2 is completely in interval1
  else if (
    interval1[0] <= interval2[0] &&
    interval2[0] <= interval1[1] &&
    (interval1[0] <= interval2[1] && interval2[1] <= interval1[1])
  ) {
    // Return 1 in-interval and 2 out-intervals
    return [
      interval2,
      [interval1[0], round(interval2[0] - decrement, 2)],
      [round(interval2[1] + increment, 2), interval1[1]]
    ];
  }
  // If two interval does not overlap at all
  else {
    // Return 1 out-interval and nothing is ins
    return [null, interval1, null];
  }
}

function get_num_binary_set(rows, col_id, separator, interval_symbol_list, dividing_number, dividing_interval_val) {
  var true_set = [];
  var false_set = [];
  for (r of rows) {
    var val_list = process_raw_val(r[0][col_id], separator);
    var value_sets = [[], []];
    for (val of val_list) {
      // Put missing char to the false value set
      if (val == MISSINGCHAR) {
        value_sets[1].push(val);
      }
      // If the row value at the column is a number
      else if (is_num(val)) {
        // If divide the row by number
        if (dividing_number != null) {
          if (val == dividing_number) {
            value_sets[0].push(String(val));
          } else {
            value_sets[1].push(String(val));
          }
        }
        // If divide the row by interval
        else {
          if (dividing_interval_val[0] <= val && val <= dividing_interval_val[1]) {
            value_sets[0].push(String(val));
          } else {
            value_sets[1].push(String(val));
          }
        }
      }
      // If the row value is an interval
      else {
        var val_interval = process_interval(interval_symbol_list, val);
        // If divide the row by a number
        if (dividing_number != null) {
          // If the number used to split is in the interval
          if (val_interval[0] <= dividing_number && dividing_number <= val_interval[1]) {
            value_sets[0].push(String(dividing_number));

            var decrement = find_smallest_change(val_interval[0], dividing_number);
            var increment = find_smallest_change(dividing_number, val_interval[1]);

            // print('\nInterval to be separated: {}, dividing_number:{}'.format(val_interval, dividing_number))

            // Divide the interval into two excluding the number used to split
            if (dividing_number != val_interval[0]) {
              var interval1 = restore_interval(val_interval[0], round(dividing_number - decrement, 2));
            } else {
              var interval1 = null;
            }

            if (dividing_number != val_interval[1]) {
              var interval2 = restore_interval(round(dividing_number + increment, 2), val_interval[1]);
            } else {
              var interval2 = null;
            }

            // print('Separated interval1:{}, interval2:{}'.format(interval1, interval2))

            // Append new intervals to false value set
            if (interval1 != null) {
              value_sets[1].push(interval1);
            }
            if (interval2 != null) {
              value_sets[1].push(interval2);
            }
          }
          // If the number used to split is not in the interval, append the interval to false value set
          else {
            value_sets[1].push(val);
          }
        }
        // If divide the row by an interval
        else {
          var all_intervals = separate_intervals(val_interval, dividing_interval_val);
          var true_interval = all_intervals[0],
            false_interval_1 = all_intervals[1],
            false_interval_2 = all_intervals[2];

          if (true_interval != null) {
            value_sets[0].push(restore_interval(true_interval[0], true_interval[1]));
          }

          if (false_interval_1 != null) {
            value_sets[1].push(restore_interval(false_interval_1[0], false_interval_1[1]));
          }

          if (false_interval_2 != null) {
            value_sets[1].push(restore_interval(false_interval_2[0], false_interval_2[1]));
          }
        }
      }
    }

    if (value_sets[0].length != 0) {
      var r_copy = [r[0].slice(), r[1].slice()];
      r_copy[0][col_id] = value_sets[0].join(separator);
      true_set.push(r_copy);
    }

    if (value_sets[1].length != 0) {
      var r_copy = [r[0].slice(), r[1].slice()];
      r_copy[0][col_id] = value_sets[1].join(separator);
      false_set.push(r_copy);
    }
  }
  return [true_set, false_set];
}

Array.prototype.remove = function() {
  var what,
    a = arguments,
    L = a.length,
    ax;
  while (L && this.length) {
    what = a[--L];
    while ((ax = this.indexOf(what)) !== -1) {
      this.splice(ax, 1);
    }
  }
  return this;
};

function divide_rows(rows, col_id, separator = '||', interval_symbol_list = ['^', '<=', '>=']) {
  var result = {}; // key is a distinct attr value in column col_id, value is a list of rows
  for (row of rows) {
    var data = row[0];
    var raw_attr_val = data[col_id];
    var attr_val_arr = process_raw_val(raw_attr_val, separator);
    // Iterate the or-split list (or a list with a single val)
    for (attr_val of attr_val_arr) {
      // Not using missing char or repeated value to split
      if (attr_val == MISSINGCHAR || Object.keys(result).includes(attr_val)) {
        continue;
      }

      result[attr_val] = [];
      var true_set = [];
      var false_set = [];
      // Numeric values
      if (NUMERIC_COL_IDS.includes(col_id)) {
        // If attribute value to split on is a number
        if (is_num(attr_val)) {
          var divided_sets = get_num_binary_set(rows, col_id, separator, interval_symbol_list, attr_val, null);
          var true_set = divided_sets[0],
            false_set = divided_sets[1];
        }

        // If attribute value to split on is an interval
        else {
          var interval_val = process_interval(interval_symbol_list, attr_val);
          var divided_sets = get_num_binary_set(rows, col_id, separator, interval_symbol_list, null, interval_val);
          var true_set = divided_sets[0],
            false_set = divided_sets[1];
        }
      }

      // Categorical value
      else {
        for (r of rows) {
          var val_arr = process_raw_val(r[0][col_id], separator);
          // Divide the rows into two sets
          if (val_arr.includes(attr_val)) {
            var r_copy = [r[0].slice(), r[1].slice()];
            r_copy[0][col_id] = attr_val;
            true_set.push(r_copy);
            // Divide the other non-belonging or separated values into the false set
            if (val_arr.length > 1) {
              val_arr.remove(attr_val);
              var r_copy = [r[0].slice(), r[1].slice()];
              r_copy[0][col_id] = val_arr.join(separator);
              false_set.push(r_copy);
            }
          }
          // For single-valued false set
          else {
            var r_copy = [r[0].slice(), r[1].slice()];
            false_set.push(r_copy);
          }
        }
      }
      result[attr_val].push(true_set);
      result[attr_val].push(false_set);
    }
  }
  return result;
}

function sort_obj_by_keys(unordered) {
  var ordered = {};
  Object.keys(unordered)
    .sort()
    .forEach(function(key) {
      ordered[key] = unordered[key];
    });
  return ordered;
}

function total_entropy_of_split(row_sets, class_label_col, scoref = entropy) {
  var total_row_len = 0;
  for (val_list of row_sets) {
    total_row_len += val_list.length;
  }
  var total_ent = 0;
  for (val_list of row_sets) {
    var w = val_list.length / total_row_len;
    var ent = scoref(val_list, class_label_col);
    total_ent += w * ent;
  }
  return total_ent;
}

function get_col() {
  var column_count = data_rows[0][0].length;
  if (data_rows.length > 900) {
    column_count = 20;
  } else if (data_rows.length > 500) {
    column_count = 40;
  } else if (data_rows.length > 300) {
    column_count = 80;
  }
  return column_count;
}

// Divides a set on a specific column. Can handle numeric
// or nominal values
function find_best_questions(class_id, total_score_func = total_entropy_of_split) {
  //0: current rows, 1: current class_id, 2:question object sorted by total entropy, 3: the index to track which current question was asked
  var decision_array = [];

  var class_label_col = class_id;
  decision_array.push(data_rows);
  decision_array.push(class_label_col);

  var column_count = get_col();

  //Key is totol entropy, value is [col_id, value_key]
  var q_obj = {};
  //Find the best cols
  for (var col_id = 0; col_id < column_count; col_id++) {
    if (skip_col_arr.includes(col_id)) {
      continue;
    }
    // print('\nAttribute to split:', attr_header[col_id])
    var sets = divide_rows(data_rows, col_id);
    // elapsed_time = time.time() - start_time
    // print(elapsed_time, 'Seconds')
    // print('Number of sets:', len(sets))

    var current_val = null;
    var score = null;
    for (let [val_key, row_sets] of Object.entries(sets)) {
      var sets_score = total_score_func(row_sets, class_label_col);
      if (score == null || sets_score < score) {
        score = sets_score;
        current_val = val_key;
      }
    }

    // Add to the question object to be asked
    if (score != null) {
      q_obj[score] = [col_id, current_val];
    }
  }

  decision_array.push(sort_obj_by_keys(q_obj), 0);
  decision_arrays.push(decision_array);

  console.log('Question object (sorted entropy: [col_id, value to split] ):', decision_array[2]);

  ask_question(-1);
}

function get_new_class_id(min_gain, total_score_func = total_entropy_of_split) {
  if (data_rows.length == 0) {
    return null;
  }
  var cur_class_id = decision_arrays[decisson_state_index][1];
  var cur_q_objs = decision_arrays[decisson_state_index][2];
  var cur_q_index = decision_arrays[decisson_state_index][3];

  //Set up cur and parent score to calculate gain later
  var parent_score = total_score_func([data_rows], cur_class_id);
  var current_score = Object.keys(cur_q_objs)[cur_q_index];

  var gain = parent_score - current_score;
  if (gain < min_gain) {
    if (cur_class_id > 0) {
      return (cur_class_id -= 1);
    }
    return null;
  }

  return cur_class_id;
}

function get_new_rows(set_index) {
  var cur_rows = decision_arrays[decisson_state_index][0];
  var cur_q_objs = decision_arrays[decisson_state_index][2];
  var cur_q_index = decision_arrays[decisson_state_index][3];
  var cur_col_id = cur_q_objs[Object.keys(cur_q_objs)[cur_q_index]][0];
  var cur_val = cur_q_objs[Object.keys(cur_q_objs)[cur_q_index]][1];

  return divide_rows(cur_rows, cur_col_id)[cur_val][set_index];
}
