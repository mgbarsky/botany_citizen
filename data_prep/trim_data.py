def is_valid_number(s):
    if s[0] == '-' or 'e' in s:
        return False

    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False


def create_attribute_dic(unique_values):
    attribute = ""
    attribute_dic = {}
    value_list = []
    for row in unique_values:
        attribute_value_row_list = row.split('\t')
        if attribute != attribute_value_row_list[0] and attribute != "":
            attribute_dic[attribute] = value_list
            value_list = []

        attribute = attribute_value_row_list[0].strip().replace('\n', '')
        value_list.append(attribute_value_row_list[1].strip().replace('\n', ''))  # append the trimmed value

    attribute_dic[attribute] = value_list  # handle last row of file

    return attribute_dic


def data_prettier(plant_table, attribute_dic, attribute_key_list):
    import csv
    with open('trimmed_initial_table.tsv', 'wt', newline='') as trimmed_plant_table:
        tsv_writer = csv.writer(trimmed_plant_table, delimiter='\t')

        plant_header = ['Leaf compoundness', 'Leaf type', 'Leaflet number per leaf from', 'Leaflet number per leaf to', 'Leaf shape',
         'Arrangement type', 'Leaf margin type', 'Leaf area 1 from', 'Leaf area 1 to', 'Leaf area 2 from',
         'Leaf area 2 to', 'Inflorescence type', 'Flower sex']
        tsv_writer.writerow(plant_header)

        for row in plant_table:
            value_row_list = row.split('\t')
            for i in range(len(value_row_list)):
                value_row_list[i] = value_row_list[i].strip().replace('\n', '')

            data_validator = True
            for i in range(len(value_row_list)):
                if i in [2, 3, 7, 8, 9, 10]:
                    if (not is_valid_number(value_row_list[i])) and (value_row_list[i] not in attribute_dic[attribute_key_list[i]]):
                        # in case the value is not a valid num
                        data_validator = False
                else:
                    if value_row_list[i] not in attribute_dic[attribute_key_list[i]]:
                        # in case the value in table is not in the valid value list
                        data_validator = False

                if i == 12:  # species name after 12
                    break

            if data_validator is True:
                tsv_writer.writerow(value_row_list)


def main():
    attribute_key_list = ['Leaf compoundness', 'Leaf type', 'Leaflet number per leaf', 'Leaflet number per leaf',
                      'Leaf shape', 'Leaf distribution along the shoot axis (arrangement type)',
                      'Leaf margin type',
                      'Leaf area (in case of compound leaves undefined if leaf or leaflet, undefined if petiole is in- or excluded)',
                      'Leaf area (in case of compound leaves undefined if leaf or leaflet, undefined if petiole is in- or excluded)',
                      'Leaf area (in case of compound leaves undefined if leaf or leaflet, undefined if petiole is in- or excluded)',
                      'Leaf area (in case of compound leaves undefined if leaf or leaflet, undefined if petiole is in- or excluded)',
                      'Inflorescence type',
                      'Flower sex'
                      ]  # 2, 3, 7, 8, 9, 10 can be type number

    with open('unique_values.txt', encoding='cp932', errors='ignore') as unique_values:
        attribute_dic = create_attribute_dic(unique_values)
        print(attribute_dic)

    with open('initial_table.tsv', encoding='cp932', errors='ignore') as plant_table:
        data_prettier(plant_table, attribute_dic, attribute_key_list)


main()
