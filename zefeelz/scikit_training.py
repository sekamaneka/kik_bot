import csv
import random
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.cross_validation import train_test_split
from sklearn.externals import joblib
from sklearn.linear_model import LogisticRegression

# now you can save it to a file
#joblib.dump(clf, 'filename.pkl')
# and later you can load it
#clf = joblib.load('filename.pkl')


def parser(row):
    sent = row[1].encode('utf-8', 'ignore').decode('utf-8')
    if sent == '0':
        sentiment = 'neg'
    else:
        sentiment = 'pos'
    return row[-1].strip(), sentiment


def data():
    training = []
    with open('Sentiment Analysis Dataset.csv', 'r') as csvf:
        reader = csv.reader(csvf)
        reader = list(reader)
        for row in range(0, len(reader), 500):
            sentence_tuple = parser(reader[row])
            training.append(sentence_tuple)
            print(row)
    return [i for i, v in training], [v for i, v in training]


words, labels = data()
print(labels)
vectorizer = CountVectorizer(
    analyzer='word',
    lowercase=False,
)
features = vectorizer.fit_transform(
    words
)
features_nd = features.toarray()  # for easy usage
print(features_nd)
X_train, X_test, y_train, y_test = train_test_split(
    features_nd,
    labels,
    train_size=0.90,
    random_state=1234)
log_model = LogisticRegression()
log_model = log_model.fit(X=X_train, y=y_train)
y_pred = log_model.predict(X_test)
j = random.randint(0, len(X_test) - 7)
for i in range(j, j + 7):
    ind = features_nd.tolist().index(X_test[i].tolist())
    print(y_pred[i])
    print(words[ind].strip())

from sklearn.metrics import accuracy_score
print(accuracy_score(y_test, y_pred))
