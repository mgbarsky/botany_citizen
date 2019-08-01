import clusters
import make_vectors
import prune as prune_utils
from queue import PriorityQueue
import json

METRIC = "pearson"


# Get hierarchy information from data/itemHierarchy.csv
def get_hierarchy(filename):
    data = open(filename)
    hierarchy = {}
    level1_set = set()
    level2_set = set()

    header = True
    for line in data:
        if header:
            header = False
            continue

        arr = line.rstrip().split(',')
        entry = arr[1]
        level2 = arr[2]
        level1 = arr[3]

        hierarchy[entry] = [level1, level2]
        level1_set.add(level1)
        level2_set.add(level2)

    data.close()
    return hierarchy, level1_set, level2_set


def collapse(node):
    temp = node.id
    node.id = [temp] if (temp >= 0) else []

    prune_utils.find_items(node.left, node.id)
    prune_utils.find_items(node.right, node.id)

    node.left = None
    node.right = None


def prune(current_cluster, num_clusters):
    queue = PriorityQueue()  # Store nodes, and the cost of splitting them into left/right child
    queue.put((current_cluster.distance, current_cluster))

    # Make sure this is bigger than the cumulative distance of any leaf; this is a shortcut
    # to ensure that if leaves are inserted into the queue, they have different keys
    big = 1000000

    count = 0
    while queue.qsize() < num_clusters:
        next_tuple = queue.get()
        distance = next_tuple[0]
        next_node = next_tuple[1]

        # If a leaf node ever needs to be split, num_clusters is too big
        if next_node.id >= 0:
            print("Error: Not enough leaves to accommodate {} clusters".format(num_clusters))
            return

        left_child = next_node.left
        right_child = next_node.right

        # Put the two children into the queue, marking the cost of splitting one
        queue.put((distance + left_child.distance if left_child.id < 0 else big + count, left_child))
        queue.put((distance + right_child.distance if right_child.id < 0 else big + count + 1, right_child))

        count += 2

    # (For now) collapse all remaining nodes in the queue
    while not queue.empty():
        next_node = (queue.get())[1]
        collapse(next_node)


def main():
    with open("json/{}.json".format(METRIC)) as data:
        json_obj = json.load(data)
        created_clusters = clusters.read_json(json_obj)

    labels = make_vectors.get_list("data/itemIndex.txt")
    hierarchy, level1_set, level2_set = get_hierarchy("data/itemHierarchy.csv")

    prune(created_clusters, len(level1_set))  # Prune so that there are len(level1_set) nodes
    clusters.drawdendrogram(created_clusters, labels, jpeg='img/v2_test.jpg')


if __name__ == "__main__":
    main()
