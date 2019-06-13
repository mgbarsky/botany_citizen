def count(input_name):
    genera = set()
    plant_f = open(input_name)
    for line in plant_f:
        genus = line.split()[0]
        genus = genus[0] + genus[1:].lower()
        genera.add(genus)
    return len(genera)


if __name__ == "__main__":
    print(count("output/plants.txt"))
