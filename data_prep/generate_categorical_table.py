# Take the full table (d_flower_data_full.tsv) with both categorical and numeric attributes/values
# Convert it into a table with only categorical ones
import csv
NUMERIC_COL_IDS = [5, 7, 9, 15, 19, 24, 25, 26, 33, 39, 40, 57, 60, 66, 77, 78, 79, 86, 89, 95, 103, 109, 115, 120, 121,
                   126, 127, 140, 143, 158, 172, 174, 175, 176, 179, 180, 182, 183, 185, 189, 190, 191, 193, 194, 195]


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


# Take original header and rows
# Return new header and rows with only categorical attributes/values
def trim_table(header, data_rows):
    cat_header = []
    cat_rows = [[] for i in range(len(data_rows))]

    for col_id in (range(len(header))):
        if col_id in NUMERIC_COL_IDS:
            continue

        cat_header.append(header[col_id])
        for row_index in range(len(data_rows)):
            cat_rows[row_index].append(data_rows[row_index][col_id])

    return cat_header, cat_rows


# Write table header (list) and all feature rows (list of lists) to the tsv file
def write_tsv(output_file_path, header_list, table_list):
    with open(output_file_path, 'w', encoding="utf-8", newline='') as tsv_file:
        tsv_writer = csv.writer(tsv_file, delimiter='\t')
        tsv_writer.writerow(header_list)  # Write the header
        for row in table_list:
            tsv_writer.writerow(row)


def main():
    header, data_rows = get_table('d_flower_data_full.tsv')
    print('Expected # of columns: ', len(header) - len(NUMERIC_COL_IDS))
    cat_header, cat_rows = trim_table(header, data_rows)
    print('Actual length of columns: ', len(cat_header))

    write_tsv('d_flower_data_cat.tsv',  cat_header, cat_rows)


main()
