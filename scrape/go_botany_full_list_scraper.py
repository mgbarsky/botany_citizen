# Scrape go-botany using a chrome instance
from selenium import webdriver
from bs4 import BeautifulSoup as Soup
import time

# Use long link to skip pop-up box
LINK = "https://gobotany.nativeplanttrust.org/full/non-monocots/alternate-remaining-non-monocots" \
       "/#_filters=family,genus,habitat_general,habitat,state_distribution,leaf_type_general_rn,petal_color_rn," \
       "leaf_arrangement_general_rn,leaf_blade_margin_general_rn,flower_symmetry_rn,perianth_number_rn," \
       "perianth_fusion_rn,stamen_number_rn,fruit_type_general_rn,fruit_length_rn&_view=photos&_show=flowers"
HOST_NAME = "https://gobotany.nativeplanttrust.org"  # The domain name to combine with the relative paths
CHECK_FREQUENCY = 0.25  # Number of seconds between scanning the page for new elements
MISSING_CHAR = '?'  # For replacing with missing values
SEPARATOR = ' || '  # To separate multiple values of a attribute, if any
FILE_PATH = 'flower_triple.tsv'  # The path for the output file that contains: species  attribute   value


# Convert browser element to soup object
def get_soup(browser):
    return Soup(browser.page_source, "html.parser")


# Wait for a element of class to load
def wait_load_class(browser, name):
    while len(browser.find_elements_by_class_name(name)) == 0:  # Wait until everything loads
        time.sleep(CHECK_FREQUENCY)


# Get a list of hyper links of plant detail pages
def get_plant_href(browser):
    wait_load_class(browser, "plant-img-container")
    soup_object = get_soup(browser)
    plant_object = soup_object.find("div", {"class": "plant-list"})

    plant_link_arr = []
    for a_tag in plant_object.find_all('a', href=True):
        plant_link_arr.append(HOST_NAME+a_tag['href'])  # concatenate href with the real link
    return plant_link_arr


# Return the species name and the dictionary that contains
# in the format of {'attr1':'value', 'attr2':'value1 || value2, ...', ...}
def get_plant_chara(browser):
    soup_object = get_soup(browser)
    plant_name = soup_object.find("span", {"class": "scientific"}).get_text()

    chara_dict = {}
    # Find all divs containing the description lists (that has a set of attr&value pairs we want)
    list_container_object = soup_object.find_all("div", {"class": "characteristics"})

    # Iterate over all div containers except the last one (the regional distribution)
    for div_index in range(len(list_container_object)-1):
        for def_list in list_container_object[div_index].find_all("dl"):  # Iterate description lists
            # dt contains the attribute and dd contains the value(s) we want
            attribute = def_list.find("dt").get_text().replace('\n', '').strip()

            value = def_list.find("dd").get_text().replace('\n', '').strip()  # When there is a single value
            if value == 'NA':  # When value does not exit, replace with question mark
                value = MISSING_CHAR

            if def_list.find("dd").find("ul") is not None:  # In case there are multiple values in ul
                val_arr = []
                for val in def_list.find("dd").find_all("li"):
                    val_arr.append(val.get_text().replace('\n', '').strip())
                value = SEPARATOR.join(val_arr)

            chara_dict[attribute] = value

    return plant_name, chara_dict


# Take plant species name and a dictionary of its attributes & values,
# and write triples (species, attribute, value) to the file
def write_triples(plant_name, chara_dict, output_f):
    for attribute, value in chara_dict.items():
        output_f.write(plant_name+'\t'+attribute+'\t'+value+'\n')


def begin_scrape():
    browser = webdriver.Chrome()
    browser.get(LINK)  # let the browser open the page of plant list
    plant_link_arr = get_plant_href(browser)

    output_f = open(FILE_PATH, 'a', encoding="utf-8")  # Open the file for writing
    progress_count = 0
    # Iterate over all plant characteristic pages
    for plant_link in plant_link_arr:
        browser.get(plant_link)  # let the browser open each of the href link of plant details
        plant_name, chara_dict = get_plant_chara(browser)
        write_triples(plant_name, chara_dict, output_f)
        progress_count += 1

        print('Finished scraping, {}, at: {}'.format(plant_name, plant_link))
        print('Full feature: ', chara_dict)
        print('Progress: {}/{}'.format(progress_count, len(plant_link_arr)), '\n')
    output_f.close()


def main():
    begin_scrape()


main()
