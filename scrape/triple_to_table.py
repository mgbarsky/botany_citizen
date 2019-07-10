# Convert a tsv file with triples (species  attribute  value) into feature table with header
import csv

MISSING_CHAR = '?'  # For replacing with missing values
INPUT_FILE_PATH = 'flower_triple.tsv'  # The path for the input file that contains: species  attribute   value
OUTPUT_FILE_PATH = 'flower_data.tsv'  # The path for the output file that will contain: header and feature rows


# Return a header (list) with all unique attributes
def get_header(reader):
    header_list = []
    for triple_list in reader:  # each row is a triple
        if triple_list[1] not in header_list:
            header_list.append(triple_list[1])
    print('Number of attributes: ', len(header_list))
    return header_list


# Take all rows of plant triple from file
# Return table header (list) and all feature rows (list of lists)
def table_converter(file_path):
    with open(file_path, encoding="utf-8") as tsv_file:
        reader_list = list(csv.reader(tsv_file, delimiter='\t'))
        header_list = get_header(reader_list)

        # Initialize a list of '?' with size equal to # of attributes, to store values of a plant
        row_list = ['?'] * len(header_list)
        table_list = []  # to contain all row list
        for triple_index in range(len(reader_list)):
            for attr_index in range(len(header_list)):
                # If the triple has an attribute in header and a valid value
                if reader_list[triple_index][1] == header_list[attr_index] \
                        and reader_list[triple_index][1] != MISSING_CHAR:
                    row_list[attr_index] = reader_list[triple_index][2]  # replace '?' with the actual value

            # If current species name in triple differs from next one (and next one is not the last one),
            # append the row list to table list, and initialize the row list for the species in next iteration
            try:
                if reader_list[triple_index][0] != reader_list[triple_index+1][0]:
                    row_list.append(reader_list[triple_index][0])  # append the current species name to the row list
                    table_list.append(row_list)
                    row_list = ['?'] * len(header_list)

            except IndexError:
                pass
        return header_list, table_list


# Write table header (list) and all feature rows (list of lists) to the tsv file
def write_tsv(header_list, table_list):
    with open(OUTPUT_FILE_PATH, 'w', encoding="utf-8", newline='') as tsv_file:
        tsv_writer = csv.writer(tsv_file, delimiter='\t')
        tsv_writer.writerow(header_list + ['Species', 'Genus', 'Family', 'Order'])  # add levels to header
        for row in table_list:
            tsv_writer.writerow(row)


def main():
    header_list, table_list = table_converter(INPUT_FILE_PATH)
    write_tsv(header_list, table_list)


main()
