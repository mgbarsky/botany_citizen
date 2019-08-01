import clusters
import json

if __name__ == "__main__":
    docs,words,data=clusters.readfile('data/grocery_vectors.txt')

    clust = clusters.hcluster(data, distance=clusters.tanimoto)
    print('clusters by tanimoto coefficient')
    clusters.drawdendrogram(clust,docs,jpeg='img/groceries_tanimoto.jpg')

    json_obj = {}
    clusters.jsonify(clust, json_obj)
    with open("json/tanimoto.json", "w") as output:
        json.dump(json_obj, output)

    #clust=clusters.hcluster(data,distance=clusters.pearson)
    #print('clusters by pearson correlation')
    #clusters.drawdendrogram(clust,docs,jpeg='groceries_pearson.jpg')

    #clust = clusters.hcluster(data, distance=clusters.cosine)
    #print('clusters by cosine similarity')
    #clusters.drawdendrogram(clust,docs,jpeg='groceries_cosine.jpg')

    #clust=clusters.hcluster(data,distance=clusters.euclidean)
    #print('clusters by euclidean distance')
    #clusters.drawdendrogram(clust,docs,jpeg='groceries_euclidean.jpg')
