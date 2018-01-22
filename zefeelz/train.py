import csv
import pickle as pickle
from textblob import Blobber
from textblob.classifiers import NaiveBayesClassifier
from textblob.sentiments import NaiveBayesAnalyzer


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
        for row in range(0, len(reader), 1000):
            sentence_tuple = parser(reader[row])
            training.append(sentence_tuple)
    return training


def train():
    training = data()
    classifier = NaiveBayesClassifier(training)
    return classifier


# try:
# with open('file.pickle', 'rb') as f:
#print('About to load')
#cl = pickle.load(f)
# except FileNotFoundError:
# print('Training')
#cl = train()
# with open('file.pickle', 'wb') as f:
#pickle.dump(cl, f)


print('Data loaded.')
blobber = Blobber(analyzer=NaiveBayesAnalyzer(), classifier=train())  # , classifier = cl)
print('Data trained')
send = blobber('And i once knew you are a dick.')
print(send.sentiment)
print(send.classify())
send = blobber('You are the worst shit in the world.')
print(send.sentiment)
print(send.classify())
send = blobber('I will always love you you are the best in the world.')
print(send.sentiment)
print(send.classify())
send = blobber('The clasifier is roten.')
print(send.correct())
# print(send.classify())
# print(send.correct())
# print(send.subjectivity)
# print(send.polarity)
# print(send.correct())
print(type(send))
print(dir(send))
