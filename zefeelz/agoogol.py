"""Return sentiment analysis on given words."""

import json
import requests
import os
import sys
# import urllib

from textblob import Blobber
from textblob.sentiments import NaiveBayesAnalyzer
from flask import Flask, request, Response
from kik import KikApi, Configuration
from kik.messages import messages_from_json, TextMessage, StartChattingMessage, ScanDataMessage, StickerMessage, VideoMessage, PictureMessage, LinkMessage
from raven import Client
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

parentPath = os.path.abspath("..")
if parentPath not in sys.path:
    sys.path.insert(0, parentPath)

import utility
analyzer = SentimentIntensityAnalyzer()


@utility.app.route('/', methods=['POST'])
def incoming():
    """Handle incoming traffic."""
    if not utility.kik.verify_signature(request.headers.get('X-Kik-Signature'), request.get_data()):
        return Response(status=403)

    messages = messages_from_json(request.json['messages'])
    try:
        for message in messages:
            if isinstance(message, TextMessage):
                print(message.from_user, ':', message.body)
                print_sentiment_scores(message)
            else:
                utility.handle_secondary_message_types(message)
    except (IndexError, AttributeError) as error:
        print("No messages found.", error)
    return Response(status=200)



def response_picker(message):
    """Picks the appropriate response."""
    data = message.body
    analysis_bayes = utility.blobber(data)
    sentiment = analysis_bayes.sentiment
    subjectivity = analysis_bayes.subjectivity
    polarity = analysis_bayes.polarity
    sentiment_label = sentiment.classification
    print(sentiment)
    print(type(sentiment))
    accuracy = max(sentiment.p_pos, sentiment.p_neg)
    if polarity > 0:
        utility.send_messages(message, text_to_send="Subjectivity: {}%\nAccuracy: {}%\nPositivity: {}%".format(
            subjectivity * 100, int(accuracy * 100), int(polarity * 100)))
    if polarity < 0:
        utility.send_messages(message, text_to_send="Subjectivity: {}%\nAccuracy: {}%\nNegativity: {}%".format(
            subjectivity * 100, int(accuracy * 100), int(-polarity * 100)))
    if polarity == 0:
        utility.send_messages(message, text_to_send="Your tone is too neutral for me to determine something. Congratulations.")

def print_sentiment_scores(message):
    snt = analyzer.polarity_scores(message.body)
    utility.send_messages(message, text_to_send=str(snt))


utility.run()
