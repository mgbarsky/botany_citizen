import clusters

if __name__ == "__main__":
    docs,words,data=clusters.readfile('grocery_vectors.txt')

    clust=clusters.hcluster(data,distance=clusters.pearson)
    print('clusters by pearson correlation')
    clusters.drawdendrogram(clust,docs,jpeg='groceries_pearson.jpg')

    clust=clusters.hcluster(data,distance=clusters.tanimoto)
    print('clusters by tanimoto coefficient')
    clusters.drawdendrogram(clust,docs,jpeg='groceries_tanimoto.jpg')

    clust=clusters.hcluster(data,distance=clusters.euclidean)
    print('clusters by euclidean distance')
    clusters.drawdendrogram(clust,docs,jpeg='groceries_euclidean.jpg')
