# Take the manually edited unique_values1.tsv file
# and replace the values in the original data set with the proper values
import csv


# Return the header list and a list of table rows from file
def get_table(file_path, header=True):
    with open(file_path, encoding="utf-8") as tsv_file:
        reader = csv.reader(tsv_file, delimiter='\t')
        if header:
            header = next(reader, None)
            rows = list(reader)
            return header, rows
        rows = list(reader)
        return rows


# Take the original header and rows, return new header and rows with only attributes and values in unique_val_rows
def trim_table(header, data_rows, unique_val_rows):
    attribute_list = []
    for row_index in range(0, len(unique_val_rows), 2):
        if unique_val_rows[row_index][0] not in attribute_list:
            attribute_list.append(unique_val_rows[row_index][0])
    attribute_list += ['Species', 'Genus', 'Family', 'Order']

    trimmed_header = []
    trimmed_rows = [[] for i in range(len(data_rows))]
    for attr_index in range(len(header)):
        if header[attr_index] in attribute_list:
            trimmed_header.append(header[attr_index])
            for data_row_index in range(len(data_rows)):
                trimmed_rows[data_row_index].append(data_rows[data_row_index][attr_index])
    return trimmed_header, trimmed_rows


# Take header and data_rows
# Replace the old attribute in header and old values in data_rows with new ones in unique_val_rows
def replace_val(header, data_rows, unique_val_rows):
    for row_index in range(0, len(unique_val_rows), 2):
        for attr_index in range(len(header)-4):
            if header[attr_index] == unique_val_rows[row_index][0]:
                header[attr_index] = unique_val_rows[row_index+1][0]  # change to header with new attribute names
                for data_row in data_rows:
                    for val_index in range(len(unique_val_rows[row_index])):
                        split_vals = data_row[attr_index].split(' || ')
                        for split_val_index in range(len(split_vals)):
                            if unique_val_rows[row_index][val_index] == split_vals[split_val_index]:
                                split_vals[split_val_index] = unique_val_rows[row_index+1][val_index]
                        data_row[attr_index] = ' || '.join(split_vals)  # change to new value in a row


# Print out list of column ids with numeric values
def print_numeric_col_id(header, rows, separator=' || ', interval_symbol_list=('^', '<', '>', '<=', '>=')):
    numeric_col_list = []
    for col_id in range(len(header)-4):
        is_col_num = False
        for row in rows:
            split_values = row[col_id].split(separator)
            for val in split_values:
                for interval_symbol in interval_symbol_list:
                    split_interval = val.split(interval_symbol)
                    for interval_val in split_interval:
                        try:
                            float(interval_val)
                            is_col_num = True
                            numeric_col_list.append(col_id)
                            break
                        except ValueError:
                            pass
                    if is_col_num:
                        break
                if is_col_num:
                    break
            if is_col_num:
                break
    print('The numeric column ids: ', numeric_col_list)


# Write table header (list) and all feature rows (list of lists) to the tsv file
def write_tsv(output_file_path, header_list, table_list):
    with open(output_file_path, 'w', encoding="utf-8", newline='') as tsv_file:
        tsv_writer = csv.writer(tsv_file, delimiter='\t')
        tsv_writer.writerow(header_list)  # Write the header
        for row in table_list:
            tsv_writer.writerow(row)


def main():
    header, data_rows = get_table('d_flower_data_1.tsv')
    unique_val_rows = get_table('unique_values1.tsv', False)
    trimmed_header, trimmed_rows = trim_table(header, data_rows, unique_val_rows)
    replace_val(trimmed_header, trimmed_rows, unique_val_rows)
    print_numeric_col_id(trimmed_header, trimmed_rows)
    write_tsv('d_flower_data_full.tsv', trimmed_header, trimmed_rows)


main()

