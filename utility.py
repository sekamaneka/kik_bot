"""Helper function for my kik bots."""
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


def setup():
    """Sets up the bot."""
    with open('data.json') as d:
        config = json.load(d)
    print(config)
    app = Flask(__name__)
    kik = KikApi(config["bot_name"], config["api_key"])
    kik.set_configuration(Configuration(webhook=config["hostname"]))
    blobber = Blobber(analyzer=NaiveBayesAnalyzer())  # , classifier = cl)
    raven_client = Client(config['sentry_hook'])
    return app, blobber, config, kik


app, blobber, config, kik = setup()


def run():
    app.run(host='0.0.0.0', port=int(config["port"]), debug=False)


def send_messages(message, inc_url="", text_to_send="", instant_pic="", link=0, inc_title=""):
    """Send the search results to the client."""

    if link:
        kik.send_messages([
            LinkMessage(
                to=message.from_user,
                chat_id=message.chat_id,
                url=inc_url,
                pic_url=instant_pic,
                text=text_to_send,
                title=inc_title
            )
        ])
    else:
        kik.send_messages([
            TextMessage(
                to=message.from_user,
                chat_id=message.chat_id,
                body=text_to_send
            )
        ])


def handle_secondary_message_types(message):
    """Reply to all required messages that aren't text."""

    if isinstance(message, LinkMessage):
        send_messages(message, text_to_send="Don't try to entice me")
    if isinstance(message, StickerMessage):
        send_messages(message, text_to_send="Nice sticker!")
    if isinstance(message, VideoMessage):
        send_messages(message, text_to_send="Nice video!")
    if isinstance(message, PictureMessage):
        send_messages(message, text_to_send="Nice picture!")
    if isinstance(message, (StartChattingMessage, ScanDataMessage)):
        send_messages(message, text_to_send="Hello and welcome.")
        send_messages(message, text_to_send="This bot is your portal to an improved Emotional Intelligence.")
        send_messages(message, text_to_send="Test your texting style and match it to that of your peers.")
        send_messages(message, text_to_send="PROTIP: If you have a crush you text with don't let your texts appear more positive than theirs.")
        send_messages(message, text_to_send="I respond to any text with 3 metrics that resemble the sentiment of the text based on machine learning.")


def handle_bot_names(message):
    """Reply if a user instead of text supplies a bot username."""

    print(message.body)
    print(message.mention)
    if message.mention:
        send_messages(message, text_to_send="We are not friends with this particular bot. His past is dark.")
        return 1
    return 0


def goo_shorten_url(url):
    """Use google api to shorten results."""

    post_url = 'https://www.googleapis.com/urlshortener/v1/url?key={}'.format(config["google_api_key"])
    payload = {'longUrl': url}
    headers = {'content-type': 'application/json'}
    r = requests.post(post_url, data=json.dumps(payload), headers=headers)
    # return only the relevant link
    return json.loads(r.text)["id"]
