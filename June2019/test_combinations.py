# A Python program to print all
# Python3 code to demonstrate
# to compute all possible permutations
# using itertools.product()
import itertools

row = [['abc', '1 or 2 or 3', 'cvh', 45, 'A or B', 567, 'X or Y or Z or W'],['a','b']]

data_cols = []
perm_input = []


for col_id in range(len(row[0])):
    if 'or' in str(row[0][col_id]):
        v = row[0][col_id]
        alt_values = v.split('or')
        perm_input.append(alt_values)
        data_cols.append(col_id)

# initializing list of list
all_list = [[1, 3, 4, 5], [6, 7], [8, 10, 5], [2, 1]]

# printing lists
print("The original lists are : " ,perm_input)

# using itertools.product()
# to compute all possible permutations
permuted = list(itertools.product(*perm_input))

# printing result
print("All possible permutations are : ", permuted)


new_rows = []
labels = row[1]
for new_vals in permuted:
    new_row_data = row[0][:]
    for i in range(len(new_vals)):
        new_row_data[data_cols[i]] = new_vals[i]

    new_row = [new_row_data] + [labels[:]]
    new_rows.append(new_row)

for row in new_rows:
    print(row)


