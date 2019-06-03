# Scrape go-botany using a chrome instance
from selenium import webdriver
from bs4 import BeautifulSoup as Soup
import time

# Use long link to skip pop-up box
LINK = "https://gobotany.nativeplanttrust.org/full/non-monocots/alternate-remaining-non-\
monocots/#_filters=family,genus,habitat_general,habitat,state_distribution,leaf_type_general\
_rn,petal_color_rn,leaf_arrangement_general_rn,leaf_blade_margin_general_rn,flower_symmetry\
_rn,perianth_number_rn,perianth_fusion_rn,stamen_number_rn,fruit_type_general_rn,fruit_length\
_rn&_view=photos&_show=flowers"
CHECK_FREQUENCY = 0.25  # Number of seconds between scanning the page for new elements
TARGET_ATTRIBUTES = ["Leaf type", "Flower petal color", "Leaf arrangement", "Leaf blade edges",
                     "Flower symmetry", "Number of sepals, petals or tepals", "Fusion of sepals and petals",
                     "Stamen number", "Fruit type (general)"]
TARGET_VALUES = {"Leaf type": ["compound", "simple"],
                 "Flower petal color": ["blue to purple", "green to brown", "orange", "other",
                                        "pink to red", "white", "yellow"],
                 "Leaf arrangement": ["alternate", "basal", "opposite", "none", "whorled"],
                 "Leaf blade edges": ["lobes", "teeth", "entire"],
                 "Flower symmetry": ["radially symmetrical", "asymmetrical", "bilaterally symmetrical"],
                 "Number of sepals, petals or tepals": ['1', '2', '3', '4', '5', '0', '6', '7'],
                 "Fusion of sepals and petals": ["unfused", "fused"],
                 "Stamen number": ['0', '1', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13'],
                 "Fruit type (general)": ["dry & splits open", "dry & doesn't split open", "fleshy"]}
plant_data = {}


# Convert browser element to soup object
def get_soup(browser):
    return Soup(browser.page_source, "html.parser")


# Get list of on-screen plants
def get_plant_set(soup_object):
    plant_list = set()
    plants = soup_object.findAll("div", {"class": "in-results"})
    for plant in plants:
        name = plant.find("a").find("p", {"class": "plant-name"}).find("span", {"class": "latin"})
        plant_list.add(name.text)
    return plant_list


# Handle element loading
def get_full_plants(browser):
    wait_load_class(browser, "plant-img-container")
    soup_object = get_soup(browser)
    plant_object = soup_object.find("div", {"class": "plant-list"})
    return get_plant_set(plant_object)


# Use an attribute for a plant
def use_attribute(browser, attribute):
    value_index = 0

    while value_index < len(TARGET_VALUES[attribute]) + 1:
        find_attribute(browser, attribute)
        choices = browser.find_elements_by_class_name("choice")

        # Iterate over the radio buttons again
        i = 0
        for choice in choices:
            label = choice.find_element_by_class_name("choice-label")
            value = label.get_attribute("innerHTML")
            if value == "don't know" and value_index != len(TARGET_VALUES[attribute]) or "doesn't apply" in value:
                continue

            # If done with all actual attributes, reset the browser state
            if value == "don't know":
                choice.find_element_by_tag_name("input").click()
                browser.find_element_by_class_name("apply-btn").click()
                break

            # If at the right attribute
            if i == value_index:
                # Click radio button, then submit button
                choice.find_element_by_tag_name("input").click()
                browser.find_element_by_class_name("apply-btn").click()

                plant_set = get_full_plants(browser)
                for plant in plant_set:  # Add (feature, value) to plant
                    if attribute in plant_data[plant]:
                        plant_data[plant][attribute].append(TARGET_VALUES[attribute][i])
                    else:
                        plant_data[plant][attribute] = [TARGET_VALUES[attribute][i]]

                break

            i += 1
        value_index += 1


# Wait for a element of class to load
def wait_load_class(browser, name):
    while len(browser.find_elements_by_class_name(name)) == 0:  # Wait until everything loads
        time.sleep(CHECK_FREQUENCY)


# Seek the element of an attribute
def find_attribute(browser, attribute):
    question_box = browser.find_element_by_id("questions-go-here")
    questions = question_box.find_elements_by_tag_name("li")

    for question in questions:
        html = question.find_element_by_class_name("name").get_attribute("innerHTML")
        name = Soup(html, "html.parser").text
        if name[:-1] == attribute:
            button = question.find_element_by_tag_name("a")
            button.click()


def begin_scrape():
    browser = webdriver.Chrome(executable_path="./chromedriver")
    browser.get(LINK)
    plant_set = get_full_plants(browser)
    # Initialize keys to empty object
    for plant in plant_set:
        print(plant)
        plant_data[plant] = {}

    for attribute in TARGET_ATTRIBUTES:
        use_attribute(browser, attribute)

    for (k, v) in plant_data.items():
        print("{}: {}".format(k, v))


# Write rows to filename
def output_rows(filename):
    output_f = open(filename, 'w')

    # Write headers
    for i in range(len(TARGET_ATTRIBUTES)):
        output_f.write(TARGET_ATTRIBUTES[i] + ('\n' if i == len(TARGET_ATTRIBUTES) - 1 else '\t'))

    for plant in plant_data:
        for attribute in TARGET_ATTRIBUTES:
            if attribute in plant_data[plant]:
                value = " or ".join(plant_data[plant][attribute])
            else:
                value = '?'
            output_f.write(value + '\t')
        output_f.write(plant + '\n')
    output_f.close()


if __name__ == "__main__":
    begin_scrape()
    output_rows("flower_data.tsv")
