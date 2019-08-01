import clusters
import make_vectors
import prune as prune_tools
import json

MIN_ACCURACY = 0.6
METRIC = "pearson"


# Get clusters from itemHierarchy.csv
def get_clusters(filename):
    data = open(filename)
    given_clusters = {}
    item_hash = {}

    header = True
    for line in data:
        if header:
            header = False
            continue

        arr = line.rstrip().split(',')
        entry = arr[1]
        cluster = arr[3]

        if cluster not in given_clusters:
            given_clusters[cluster] = set()
        given_clusters[cluster].add(entry)
        item_hash[entry] = cluster

    cluster_names = [key for key in given_clusters]
    return given_clusters, item_hash, cluster_names


# Return map of {cluster names: frequency}
def frequency_template(cluster_names):
    template = {}
    for name in cluster_names:
        template[name] = 0
    return template


# Label each node with a vector of counts per cluster
def label_nodes(clust, labels, item_hash, cluster_names):
    # Return true if leaf node
    template = frequency_template(cluster_names)
    # Leaf
    if clust.id >= 0:
        cluster_name = item_hash[labels[clust.id]]
        template[cluster_name] = 1
        clust.label = template
    else:
        label_nodes(clust.left, labels, item_hash, cluster_names)
        label_nodes(clust.right, labels, item_hash, cluster_names)
        for key in template:
            template[key] += clust.left.label[key] + clust.right.label[key]
        clust.label = template


# Prune clusters
def prune(clust, given_clusters, min_acc, min_coverage):
    total_entries = 0  # Total entries at this node
    best_count = 0  # Highest count means best accuracy
    best_key = None  # Target cluster name

    # Find total_entries, best_count, and best_key
    for key in clust.label:
        if clust.label[key] > best_count:
            best_count = clust.label[key]
            best_key = key
        total_entries += clust.label[key]

    accuracy = float(best_count)/total_entries
    coverage = float(best_count)/len(given_clusters[best_key])
    if accuracy >= min_acc and coverage >= min_coverage:
        # Parent
        if clust.id < 0:
            # If there no better accuracy and coverage values down this path, merge the left and right branches
            if not prune(clust.left, given_clusters, accuracy, coverage) and \
                    not prune(clust.right, given_clusters, accuracy, coverage):
                clust.id = []

                prune_tools.find_items(clust.left, clust.id)
                prune_tools.find_items(clust.right, clust.id)

                # Now that the IDs have been merged, delete the branches
                clust.left = None
                clust.right = None

        return True  # There are better accuracies/coverages down this path

    if clust.id < 0:
        better_left = prune(clust.left, given_clusters, min_acc, min_coverage)
        better_right = prune(clust.right, given_clusters, min_acc, min_coverage)
        if better_left or better_right:
            return True

    return False  # No better accuracy/coverage down this path


def main():
    given_clusters, item_hash, cluster_names = get_clusters("data/itemHierarchy.csv")
    with open("json/{}.json".format(METRIC)) as data:
        json_obj = json.load(data)
        created_clusters = clusters.read_json(json_obj)
    labels = make_vectors.get_list("data/itemIndex.txt")

    label_nodes(created_clusters, labels, item_hash, cluster_names)
    prune(created_clusters, given_clusters, MIN_ACCURACY, 0)
    clusters.drawdendrogram(created_clusters, labels, jpeg='img/{}_experiment.jpg'.format(METRIC))


if __name__ == "__main__":
    main()
