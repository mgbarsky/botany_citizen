# A Python program to print all
# Python3 code to demonstrate
# to compute all possible permutations
# using itertools.product()
import itertools

# initializing list of list
all_list = [[1, 3, 4], [6, 7, 9], [8, 10, 5]]

# printing lists
print("The original lists are : " + str(all_list))

# using itertools.product()
# to compute all possible permutations
res = list(itertools.product(*all_list))

# printing result
print("All possible permutations are : " + str(res))