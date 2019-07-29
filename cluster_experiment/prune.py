import clusters


def find_items(clus, id_list):
    if clus is None:
        return

    id_list.append(clus.id)
    find_items(clus.left, id_list)
    find_items(clus.right, id_list)


def collapse(clus, depth, target):
    if clus is None:
        return

    if depth == target:
        temp = clus.id
        clus.id = [temp]

        find_items(clus.left, clus.id)
        find_items(clus.right, clus.id)

        clus.left = None
        clus.right = None
    else:
        collapse(clus.left, depth + 1, target)
        collapse(clus.right, depth + 1, target)


if __name__ == "__main__":
    docs,words,data=clusters.readfile('grocery_vectors.txt')

    clust=clusters.hcluster(data,distance=clusters.pearson)
    collapse(clust, 0, 2)
    clusters.drawdendrogram(clust,docs,jpeg='pearson_depth2.jpg')

    clust = clusters.hcluster(data, distance=clusters.cosine)
    collapse(clust, 0, 2)
    clusters.drawdendrogram(clust, docs, jpeg='cosine_depth2.jpg')
