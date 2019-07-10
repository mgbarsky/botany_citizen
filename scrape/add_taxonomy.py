# Add full taxonomy to flower_data.tsv
import json
import csv
plant_json = None
taxonomy_map = {}


def recur(element, path):
    if isinstance(element, list):
        taxonomy_map[path[0]] = path
    else:
        for key in element:
            recur(element[key], [key] + path)


# Merge data from two files to generate taxonomy map
def generate_map(filename, filename2):
    global plant_json
    input_f = open(filename, encoding="utf-8")
    plant_json = json.load(input_f)
    input_f.close()
    recur(plant_json, [])

    # Check if genus missing, is so add them
    with open(filename2, 'r', encoding="utf-8") as csv_file:
        # creating a csv reader object
        csv_reader = csv.reader(csv_file)

        # extracting each data row one by one
        header = True
        for row in csv_reader:
            # Skip the header
            if header:
                header = False
                continue

            if row[0] not in list(taxonomy_map.keys()):
                taxonomy_map[row[0]] = row


def taxonomy_table(input_name, output_name):
    input_f = open(input_name, encoding="utf-8")
    output_f = open(output_name, 'w', encoding="utf-8")

    header = True
    row_counter = 0  # count the number of rows in flower table
    for line in input_f:
        if header:
            header = False
            output_f.write(line)
            continue
        row_counter += 1
        arr = line.rstrip().split('\t')
        species = arr[-1]
        genus = species.split(' ')[0]

        if genus in taxonomy_map:
            path = taxonomy_map[genus]
            arr += path
        else:
            print("Path for {} not found! at row {}".format(genus, row_counter))

        output_f.write('\t'.join(arr) + '\n')
    input_f.close()
    output_f.close()


if __name__ == "__main__":
    generate_map("taxonomy2.json", "usda_taxonomy.csv")
    print(taxonomy_map)
    taxonomy_table("flower_data.tsv", "d_flower_data.tsv")
