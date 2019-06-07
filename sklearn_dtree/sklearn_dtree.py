from sklearn.feature_extraction import DictVectorizer
from sklearn import tree
from sklearn import preprocessing
import csv


# Read the tsv file and
def tsv_reader(file_path):
    plant_data = open(file_path, 'rt')
    reader = csv.reader(plant_data, delimiter='\t')
    headers = next(reader)
    return reader, headers


# Get the feature dic in each row & a list of class labels, the plant names
def get_feature_and_label_lists(reader, headers):
    feature_list = []
    label_list = []
    for row in reader:
        label_list.append(row[len(row)-1])
        row_dic = {}
        for i in range(0, len(row)-1):
            row_dic[headers[i]] = row[i]
        feature_list.append(row_dic)
    # print(featureList)
    # print(labelList)
    return feature_list, label_list


def list_vectorizer(feature_list, label_list):
    # Vectorize features
    vec = DictVectorizer()
    dummy_x = vec.fit_transform(feature_list).toarray()  # convert into a matrix of dummy vectors for building dtree
    # print("dummyX: " + str(dummyX))
    # print(vec.get_feature_names())

    # Vectorize class labels
    lb = preprocessing.LabelBinarizer()
    dummy_y = lb.fit_transform(label_list)
    # print("dummyY: " + str(dummyY))
    return vec, dummy_x, dummy_y


# Using decision tree for classification
def build_tree(vec, dummy_x, dummy_y):
    # Gini index (CART) by default; 'entropy' = information gain (ID3);
    clf = tree.DecisionTreeClassifier(criterion='entropy')
    clf = clf.fit(dummy_x, dummy_y)
    # print("clf: " + str(clf))

    # Visualize model
    # To convert .dot to visualized pdf, using then command: dot -Tpdf plant_dtree.dot -o plant_dtree.pdf
    with open("plant_dtree.dot", 'w') as f:
        tree.export_graphviz(clf, feature_names=vec.get_feature_names(), out_file=f)
    return clf


# Predict an element in a presumable testing set
def plant_predictor(clf, label_list, new_row_x):
    predicted_y = clf.predict(new_row_x.reshape(1, -1))
    # print("predictedY: " + str(predicted_y))
    predicted_y_1d = predicted_y[0].tolist()
    for plant_index in range(len(predicted_y_1d)):
        plant_bool = predicted_y_1d[plant_index]
        if plant_bool == 1:
            print("Your plant is:", label_list[plant_index])


def main():
    reader, headers = tsv_reader('flower_data.tsv')
    feature_list, label_list = get_feature_and_label_lists(reader, headers)
    vec, feature_dummy_x, label_dummy_y = list_vectorizer(feature_list, label_list)
    clf = build_tree(vec, feature_dummy_x, label_dummy_y)

    # Change a few values of the first row of the training set and use for testing
    new_row_x = feature_dummy_x[0, :]
    # print("oneRowX: " + str(oneRowX))
    new_row_x[0] = 1
    new_row_x[2] = 0
    new_row_x[10] = 0
    new_row_x[20] = 1
    # print("newRowX: " + str(newRowX))

    plant_predictor(clf, label_list, new_row_x)


main()
