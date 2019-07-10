#  Merge Wiki taxonomy json with WorldFlora taxonomy json (from species to order)
############ NOT FINISHED DUE TO THE BAD QUALITY OF WIKI TAXONOMY FILES##############

import json


#  Parse the json files into dictionary and return them
def parse_json(input_file1, input_file2):
    with open(input_file1, encoding="utf-8") as f1:
        wiki_dict = json.load(f1)
    with open(input_file1, encoding="utf-8") as f2:
        world_flora_dic = json.load(f2)
    return wiki_dict, world_flora_dic


def merge_json(wiki_dict, world_flora_dic):
    new_dict = {}

    return new_dict


def save_json(new_dict):
    with open('taxonomy3.json', 'w') as outfile:
        json.dump(new_dict, outfile)


def main():
    wiki_dict, world_flora_dic = parse_json('taxonomy.json', 'taxonomy2.json')
    print(wiki_dict, world_flora_dic)
    exit(1)
    new_dict = merge_json(wiki_dict, world_flora_dic)
    save_json(new_dict)


main()
