# Find all unique values for each attribute and output to unique_values.tsv
import csv


# Return the header list and a list of table rows from file
def get_table(file_path):
    with open(file_path, encoding="utf-8") as tsv_file:
        reader = csv.reader(tsv_file, delimiter='\t')
        header = next(reader, None)
        rows = list(reader)
        return header, rows


# Take all rows of table and return a list of unique value list for each attribute
def get_unique_values(rows):
    val_col_list = []
    for col_index in range(len(rows[0])-4):
        unique_val_list = []
        for row in rows:
            if '||' in row[col_index]:
                vals = row[col_index].split('||')
                for val in vals:
                    if val.strip() not in unique_val_list:
                        unique_val_list.append(val.strip())

            elif row[col_index] != '?' and row[col_index].strip() not in unique_val_list:
                unique_val_list.append(row[col_index].strip())

        val_col_list.append(unique_val_list)
    return val_col_list


# Write table header (list) and all unique value rows to the tsv file
def write_tsv(header_list, table_list, out_put_file_path):
    with open(out_put_file_path, 'w', encoding="utf-8", newline='') as tsv_file:
        tsv_writer = csv.writer(tsv_file, delimiter='\t')
        tsv_writer.writerow(header_list[0:-4])
        # Transform col into row
        for col_index in range(len(max(table_list, key=len))):
            row_list = []
            for row in table_list:
                try:
                    row_list.append(row[col_index])
                except IndexError:
                    row_list.append('')
            tsv_writer.writerow(row_list)


def main():
    header, rows = get_table('d_flower_data_1.tsv')
    unique_val_list = get_unique_values(rows)
    write_tsv(header, unique_val_list, 'unique_values.tsv')
    for l in unique_val_list:
        print(l)


main()
