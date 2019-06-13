def get_unique_values(file_name,
                      key_col_id, val_col_id=None,
                      has_header=True):
    d = {}
    f = open(file_name, errors='ignore')
    count = 0
    for line in f:
        if has_header and count == 0:
            count +=1
            continue
        line = line.strip()
        line_arr = line.split(",")
        key = line_arr[key_col_id]
        val = 1
        if val_col_id is not None:
            val = line_arr[val_col_id]

        d[key] = val
        count += 1

    return d


def get_species():
    d  = get_unique_values("flower_species.csv",5,6)
    d_list = [(key,val) for key,val in d.items()]
    print(d_list[:10])
    return d


if __name__ == "__main__":
    d = get_species()
    print(len(d))

