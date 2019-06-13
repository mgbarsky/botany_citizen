# Output all collected info into files


# Frequencies
def output_frequencies(path, frequencies):
    output_f = open(path, "w", encoding="latin1")

    # Sort frequencies when writing them to the file
    freq_list = [[k, v] for (k, v) in frequencies.items()]
    freq_list.sort(key=lambda x: x[1], reverse=True)

    for tup in freq_list:
        output_f.write("{}: {}%\n".format(tup[0], str(tup[1])))
    output_f.close()


# List of plants
def output_plants(path, plant_dict):
    output_f = open(path, "w", encoding="latin1")
    for plant in plant_dict:
        output_f.write("{}\n".format(plant))
    output_f.close()


# Plants and their attributes
def output_attributes(path, plant_dict):
    output_f = open(path, "w", encoding="latin1")
    for plant in plant_dict:
        output_f.write("{}\n".format(plant))
        for tup in plant_dict[plant]:
            output_f.write("{}\t{}\n".format(tup[0], tup[1]))
        output_f.write('\n')
    output_f.close()
