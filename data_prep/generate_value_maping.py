# Take flower table
# Map each unique value of an attribute to a integer
import json
import csv


# Return the header list/a list of table rows from file
def get_table(file_path, header=True):
    with open(file_path, encoding="utf-8") as tsv_file:
        reader = csv.reader(tsv_file, delimiter='\t')
        if header:
            header = next(reader, None)
            rows = list(reader)
            return header, rows
        rows = list(reader)
        return rows


# Take the original table
# Return list of lists with unique value pairs in the format of [[val_id, value], ...]
def generate_map(header, data_rows):
    mapping = []
    unique_values = []
    val_id = 0
    # Assign '?' with id 0
    mapping.append([0, '?'])

    for col_id in range(len(header)):
        for row in data_rows:
            row_values = row[col_id].split('||')
            for val in row_values:
                if val != '?' and val not in unique_values:
                    unique_values.append(val)
                    val_id += 1
                    map_row = []
                    map_row.append(val_id)
                    map_row.append(val)
                    mapping.append(map_row)

    return mapping


# Map the table with value ids
def map_table(header, data_rows, mappings):
    for col_id in range(len(header)):
        for row_index in range(len(data_rows)):
            row_values = data_rows[row_index][col_id].split('||')
            for val_index in range(len(row_values)):
                for mapping in mappings:
                    if row_values[val_index] == mapping[1]:
                        row_values[val_index] = str(mapping[0])
            data_rows[row_index][col_id] = '||'.join(row_values)


# Write table header (list) and all feature rows (list of lists) to the tsv file
def write_tsv(output_file_path, header_list, table_list):
    with open(output_file_path, 'w', encoding="utf-8", newline='') as tsv_file:
        tsv_writer = csv.writer(tsv_file, delimiter='\t')
        tsv_writer.writerow(header_list)  # Write the header
        for row in table_list:
            tsv_writer.writerow(row)


def main():
    header, data_rows = get_table('d_flower_data_cat.tsv')
    mappings = generate_map(header, data_rows)
    map_table(header, data_rows, mappings)

    write_tsv('value_map.tsv', ['Value ID', 'Value'], mappings)
    write_tsv('d_flower_data_mapped.tsv', header, data_rows)


main()

