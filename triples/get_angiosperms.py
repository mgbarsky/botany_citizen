import json


# Get all angiosperms
def get_plant_list(plant_obj):
    if isinstance(plant_obj, list):  # If at the genus
        return plant_obj
    else:
        plant_list = []
        for key in plant_obj:
            plant_list += get_plant_list(plant_obj[key])
        return plant_list


def get_obj(input_name):
    json_file = open(input_name)
    tax = json.load(json_file)

    return tax["Plantae"]["Angiosperms"]


def write_to_file(plant_list, output_name):
    output_file = open(output_name, "w")
    for plant in plant_list:
        output_file.write(plant + '\n')
    output_file.close()


if __name__ == "__main__":
    taxonomy = get_obj("output/taxonomy.json")
    p = get_plant_list(taxonomy)
    write_to_file(p, "output/angiosperms.txt")
