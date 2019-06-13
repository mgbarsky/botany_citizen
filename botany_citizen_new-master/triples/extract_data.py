# Extract info from the 3 data sets, takes around 1.5-2 minutes to run
import utils
import output


# Return a dict of format {Plant name: [(trait, value)]}
def get_dict(filename_list, name_index=6, trait_index=10, val_index=14):
    plant_dict = {}
    
    # Iterate over all files, appending to plant_dict
    for filename in filename_list:
        input_f = open(filename, encoding="latin1")
        
        for line in input_f:
            arr = line.split('\t')
            # Skip reference lines and header, indicated by an empty trait
            if arr[trait_index] == '' or arr[trait_index] == 'TraitName':
                continue
    
            plant_name = arr[name_index]
            trait = arr[trait_index]
            value = arr[val_index]
            if plant_name not in plant_dict:
                plant_dict[plant_name] = []
            plant_dict[plant_name].append((trait, value))
        input_f.close()
    
    return plant_dict


# Filter out plants which have fewer than cutoff unique features
def filter_dict(plant_dict, cutoff=5):
    new_dict = {}
    for plant in plant_dict:
        attributes = set()  # Uniqueness
        for tup in plant_dict[plant]:
            attributes.add(tup[0])
        if len(attributes) < cutoff:
            continue
        new_dict[plant] = list(plant_dict[plant])
    return new_dict


# Filter out plants which aren't angiosperms
def filter_angiosperms(plant_dict, input_name):
    # Read angiosperms into a set
    angiosperms = set()
    input_f = open(input_name)
    for line in input_f:
        angiosperms.add(line.rstrip())
    input_f.close()

    # Filter
    new_dict = {}
    for plant in plant_dict:
        if plant in angiosperms:
            new_dict[plant] = plant_dict[plant]
    return new_dict


if __name__ == "__main__":
    p_dict = get_dict(["../flower_data/6390.txt", "../flower_data/6403.txt", "../flower_data/6404.txt"])
    p_dict = filter_dict(p_dict)
    p_dict = filter_angiosperms(p_dict, "output/angiosperms/angiosperms.txt")
    frequencies = utils.get_frequencies(p_dict)

    # Output to files
    output.output_plants("output/angiosperms/plants.txt", p_dict)
    output.output_attributes("output/angiosperms/attributes.txt", p_dict)
    output.output_frequencies("output/angiosperms/frequencies.txt", frequencies)
