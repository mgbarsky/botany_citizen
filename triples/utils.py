# Get frequencies of attributes
def get_frequencies(plant_dict):
    frequencies = {}  # First keep count of how many times an attribute appears
    count = 0  # Keep track of the number of plants

    for plant in plant_dict:
        plant_attributes = set()  # Don't count duplicate attributes (such as a flower having 2 colors)
        plant_tuples = plant_dict[plant]

        for tup in plant_tuples:
            attribute = tup[0]
            if attribute in plant_attributes:
                continue

            if attribute not in frequencies:
                frequencies[attribute] = 1
            else:
                frequencies[attribute] += 1
            plant_attributes.add(attribute)
        count += 1

    # Then divide by count to get a percentage
    for attribute in frequencies:
        frequencies[attribute] /= float(count)/100

    return frequencies


# Nicely print the attribute frequencies
def print_frequencies(frequencies):
    for k, v in frequencies.items():
        print("{}: {}%".format(k, str(v)))


# Print the attributes for each plant
def print_attributes(plant_dict):
    for plant in plant_dict:
        print("{} has the following features:".format(plant))
        for t in plant_dict[plant]:
            print(t)
        print('')
