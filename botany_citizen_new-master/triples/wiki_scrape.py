# Scrape plant hierarchy from Wikipedia, takes around an hour to run
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup as Soup
import json

WIKIPATH = "https://en.wikipedia.org/wiki/"
TABLE_CLASS = "infobox biota"
taxonomy = {}
genus_path = {}  # Hash genus to its respective list to it to minimize requests to the Wiki


def simple_get(url):
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        print("Error during requests to {0} : {1}".format(url, str(e)))
        return None


def is_good_response(resp):
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


# Return bs4 object
def get_soup(url):
    raw = simple_get(url)
    return Soup(raw, "html.parser") if raw is not None else None


# Get text from a Wiki element, bold -> italic -> everything
def get_text(element):
    bold = element.find('b')
    italic = element.find('i')
    if bold is not None:
        text = bold.text
    elif italic is not None:
        text = italic.text
    else:
        text = element.text
    return text.rstrip().replace(':', '')  # Remove newlines and colons


def get_info_box(page):
    if page is None:
        return None
    return page.find("table", {"class": TABLE_CLASS})


# Scrape plant from Wiki
def get_from_wiki(plant, genus):
    current_level = taxonomy

    page = get_soup(WIKIPATH + genus + "_(plant)")  # Check the plant prefix first for safety
    info_box = get_info_box(page)
    if info_box is None:
        page = get_soup(WIKIPATH + genus)  # Then try the normal link
        info_box = get_info_box(page)
        if info_box is None:
            print("Could not find a proper wiki page for {}!".format(genus))
            genus_path[genus] = None
            return

    for tr in info_box.findAll("tr"):
        tds = list(tr.findAll("td"))
        if len(tds) != 2:  # Ignore labels not in a pair
            continue
        current_class = get_text(tds[0])
        class_name = get_text(tds[1])

        if current_class != "Genus":
            if class_name not in current_level:
                current_level[class_name] = {}
            current_level = current_level[class_name]
        else:
            if class_name not in current_level:
                current_level[class_name] = []
            current_level = current_level[class_name]
            break

    try:
        current_level.append(plant)
    except AttributeError:  # Very rarely happens, if page formatting is strange
        return

    genus_path[genus] = current_level


# Use existing genus path to place plant
def use_path(plant, genus):
    genus_list = genus_path[genus]
    if genus_list is None:  # No page for genus
        return
    genus_list.append(plant)


# Scrape a single plant
def update_taxonomy(plant):
    genus = plant.split()[0]
    if genus not in genus_path:
        get_from_wiki(plant, genus)
    else:
        if use_path(plant, genus) is False:  # If there is an inconsistency
            get_from_wiki(plant, genus)


def main(input_name, output_name):
    plant_f = open(input_name)
    count = 0
    for line in plant_f:
        name = line.rstrip()
        update_taxonomy(name[0] + name[1:].lower())  # Convert everything except first character to lowercase

        if count % 500 == 0:
            print(count)
        count += 1
    plant_f.close()

    with open(output_name, "w") as write_file:  # Dump taxonomy into json
        json.dump(taxonomy, write_file)


if __name__ == "__main__":
    main("output/plants.txt", "output/taxonomy.json")
