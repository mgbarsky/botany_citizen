# Reads attributes file and outputs a table, takes around 20 seconds to run
import get_angiosperms

# Attributes to use in the table
ATTRIBUTES = ["Leaf compoundness", "Leaf type", "Leaflet number per leaf", "Leaf shape",
              "Leaf distribution along the shoot axis (arrangement type)", "Flower color", "Leaf margin type",
              "Leaf area (in case of compound leaves: leaflet, undefined if petiole is in- or excluded)",
              "Leaf area (in case of compound leaves: leaf, undefined if petiole in- or excluded)",
              "Inflorescence type", "Flower sex"]
ALTERNATE_NAMES = {"Leaf distribution along the shoot axis (arrangement type)": "Arrangement type",
                   "Leaf area (in case of compound leaves: leaflet, undefined if petiole is in- or excluded)":
                       "Leaf area 1",
                   "Leaf area (in case of compound leaves: leaf, undefined if petiole in- or excluded)":
                       "Leaf area 2"}
# Make an attribute set to speed things up
ATTRIBUTE_SET = set()
for attribute in ATTRIBUTES:
    if attribute not in ALTERNATE_NAMES:
        ATTRIBUTE_SET.add(attribute)
    else:
        ATTRIBUTE_SET.add(ALTERNATE_NAMES[attribute])
FEATURE_THRESHOLD = 4  # Entries with less than 4 recorded features are excluded
# Numeric attributes to express as a range
RANGE_ATTRIBUTES = {"Leaflet number per leaf", "Leaf area 1", "Leaf area 2"}
# Plant names hashed to a list of their path in the hierarchy
PLANT_PATHS = {}


# Generate plant paths from JSON object
def get_plant_paths(plant_obj, current_path):
    if isinstance(plant_obj, list):  # If at the genus
        for plant in plant_obj:
            PLANT_PATHS[plant] = current_path
    else:
        for key in plant_obj:
            get_plant_paths(plant_obj[key], [key.replace(' ', '').split('[')[0]] + current_path)  # Remove Wiki citing


# Return feature if not in ALTERNATE_NAMES, else the alternate name
def get_alternate(feature):
    if feature not in ALTERNATE_NAMES:
        return feature
    return ALTERNATE_NAMES[feature]


# Generate multiple plants given multiple observations from features using recursive backtracking
def generate_plants(characteristics, name, plant, plants, index=0):
    if index == len(ATTRIBUTES):  # If at the endpoint
        plant += [name] + PLANT_PATHS[name]
        plants.append(plant)
    else:
        current_attribute = get_alternate(ATTRIBUTES[index])
        values = characteristics[current_attribute]
        if current_attribute not in RANGE_ATTRIBUTES:
            if len(values) == 0:  # Missing data
                values.add('?')
            for value in values:
                new_plant = plant + [value]
                generate_plants(characteristics, name, new_plant, plants, index + 1)
        else:  # Express this attribute as a range
            min_val = min(values) if len(values) > 0 else '?'
            max_val = max(values) if len(values) > 0 else '?'
            new_plant = plant + [min_val, max_val]
            generate_plants(characteristics, name, new_plant, plants, index + 1)


# Get a "template": Attributes hashed to an empty set
def get_attribute_template():
    template = {}
    for feature in ATTRIBUTES:
        template[get_alternate(feature)] = set()
    return template


# Get table from input file
def get_table(filename):
    input_f = open(filename, encoding="latin1")
    current_plant = None
    current_plant_attributes = get_attribute_template()  # Attribute hashed to list of values
    current_count = 0  # Number of recorded values for current plant
    plants = []
    for line in input_f:
        if current_plant is None:
            current_plant = line.rstrip()
        else:
            if len(line.rstrip()) == 0:
                if current_count >= FEATURE_THRESHOLD:
                    generate_plants(current_plant_attributes, current_plant, [], plants)

                current_plant_attributes = get_attribute_template()
                current_count = 0
                current_plant = None
            else:
                line_arr = line.rstrip().split('\t')
                if len(line_arr) < 2:  # Person didn't enter any data for the attribute
                    continue
                [feature, value] = line_arr
                feature = get_alternate(feature)
                if feature not in ATTRIBUTE_SET:  # Only use features in the set
                    continue

                current_plant_attributes[feature].add(value)
                current_count += 1
    input_f.close()

    return plants


# Output table into a .tsv
def table_to_tsv(output, table):
    output_f = open(output, "w", encoding="latin1")

    # Write headers
    for i in range(len(ATTRIBUTES)):
        feature = get_alternate(ATTRIBUTES[i])
        output_f.write(feature + ('\n' if i == len(ATTRIBUTES) - 1 else '\t'))
    # Rest of the table
    for row in table:
        for i in range(len(row)):
            output_f.write(row[i] + ('\n' if i == len(row) - 1 else '\t'))
    output_f.close()


if __name__ == "__main__":
    taxonomy = get_angiosperms.get_obj("output/taxonomy.json")
    get_plant_paths(taxonomy, [])
    rows = get_table("output/angiosperms/attributes.txt")
    table_to_tsv("output/angiosperms/initial_table.tsv", rows)
    print("Number of entries: {}".format(str(len(rows))))
