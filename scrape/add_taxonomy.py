# Add full taxonomy to flower_data.tsv
import json

plant_json = None
taxonomy_map = {}


def recur(element, path):
    if isinstance(element, list):
        taxonomy_map[path[0]] = path
    else:
        for key in element:
            recur(element[key], [key] + path)


def generate_map(filename):
    global plant_json
    input_f = open(filename, encoding="utf-8")
    plant_json = json.load(input_f)
    input_f.close()

    recur(plant_json, [])


def taxonomy_table(input_name, output_name):
    input_f = open(input_name, encoding="utf-8")
    output_f = open(output_name, 'w', encoding="utf-8")

    header = True
    for line in input_f:
        if header:
            header = False
            output_f.write(line)
            continue
        arr = line.rstrip().split('\t')
        species = arr[-1]
        genus = species.split(' ')[0]
        if genus in taxonomy_map:
            path = taxonomy_map[genus]
            arr += path
        else:
            print("Path for {} not found!".format(genus))
            continue
        output_f.write('\t'.join(arr) + '\n')
    input_f.close()
    output_f.close()


if __name__ == "__main__":
    generate_map("taxonomy2.json")
    taxonomy_table("flower_data.tsv", "d_flower_data.tsv")
