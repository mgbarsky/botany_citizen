def get_list(filename):
    item_list = []
    data = open(filename, encoding="latin1")
    for line in data:
        item_list.append(line.rstrip())

    data.close()
    return item_list


def make_vectors(filename, item_list):
    # Initial empty vector for each grocery
    vectors = [list() for i in range(len(item_list))]
    data = open(filename, encoding="latin1")
    count = 0
    for line in data:
        for vector in vectors:
            vector.append(0)  # Add another entry to all vectors

        arr = line.rstrip().split('] ')  # Ignore "[num]"
        arr = arr[1].split(', ')
        for index in arr:
            vectors[int(index) - 1][count] = 1
        count += 1

    data.close()
    return vectors


def write_vectors(filename, vectors, item_list):
    output = open(filename, 'w', encoding="latin1")
    attributes = ['t' + str(i + 1) for i in range(len(vectors[0]))]
    output.write('\t' + '\t'.join(attributes) + '\n')

    count = 0
    for vector in vectors:
        string_vector = [str(vector[i]) for i in range(len(vector))]
        output.write(item_list[count] + '\t' + '\t'.join(string_vector) + '\n')
        count += 1

    output.close()


def main():
    item_list = get_list("data/itemIndex.txt")
    vectors = make_vectors("data/groceries_no_decode.txt", item_list)
    write_vectors("data/grocery_vectors.txt", vectors, item_list)


if __name__ == "__main__":
    main()
