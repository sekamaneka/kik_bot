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


def print_sentiment_scores(message):
    """Calculate sentiment score and send it."""
    snt = analyzer.polarity_scores(message.body)
    text = "Your Score: {}\n".format(snt['compound'])
    utility.send_messages(message, text_to_send=text)


utility.run()
