from selenium import webdriver
from bs4 import BeautifulSoup as Soup
import time
import json

LINK = "http://www.worldfloraonline.org/classification"
STOPPING_DEPTH = 4
CHECK_FREQUENCY = 0.1
data = {}
data2 = {}


# Wait for a element of class to load
def wait_load_class(element, name):
    count = 0
    while len(element.find_elements_by_class_name(name)) == 0:  # Wait until everything loads
        time.sleep(CHECK_FREQUENCY)
        count += 1

        if count == 50:
            return


def dfs(element, current, depth):
    id_list = []
    name_list = []
    wait_load_class(element, "jstree-closed")
    lis = element.find_elements_by_class_name("jstree-closed")
    for li in lis:
        name = Soup(li.get_attribute("innerHTML"), "html.parser").text[2:]
        if depth != STOPPING_DEPTH - 1:
            id_list.append(li.get_attribute("id"))
            name_list.append(name)
            button = li.find_element_by_tag_name("ins")
            browser.execute_script("arguments[0].click();", button)
        else:
            current.append(name)

    if depth == STOPPING_DEPTH - 1:
        return

    for i in range(len(id_list)):
        new_element = element.find_element_by_id(id_list[i])
        if depth < 2:
            current[name_list[i]] = {}
        elif depth == 2:
            current[name_list[i]] = []

        # Recursion step
        node = current[name_list[i]]
        dfs(new_element, node, depth + 1)

        browser.execute_script("""
        var element = arguments[0];
        element.parentNode.removeChild(element);
        """, new_element)


if __name__ == "__main__":
    browser = webdriver.Chrome(executable_path="./chromedriver")
    browser.get(LINK)

    dfs(browser, data, 0)
    try:
        dfs(browser, data2, 0)
        print('Run twice')
    except:
        pass

    print(data)
    print(data2)

    with open('taxonomy2.json', 'w') as json_file:
        json.dump(data, json_file)

    with open('taxonomy3.json', 'w') as json_file2:
        json.dump(data2, json_file2)
