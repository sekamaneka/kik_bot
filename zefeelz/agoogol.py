"""Return sentiment analysis on given words."""

import json
import requests
# import urllib

from textblob import Blobber
from textblob.sentiments import NaiveBayesAnalyzer
from flask import Flask, request, Response
from kik import KikApi, Configuration
from kik.messages import messages_from_json, TextMessage, StartChattingMessage, ScanDataMessage, StickerMessage, VideoMessage, PictureMessage, LinkMessage
from raven import Client

with open('data.json') as d:
    config = json.load(d)
print(config)
app = Flask(__name__)
kik = KikApi(config["bot_name"], config["api_key"])
kik.set_configuration(Configuration(webhook=config["hostname"]))
blobber = Blobber(analyzer=NaiveBayesAnalyzer())  # , classifier = cl)


@app.route('/', methods=['POST'])
def incoming():
    """Handle incoming traffic."""
    if not kik.verify_signature(request.headers.get('X-Kik-Signature'), request.get_data()):
        return Response(status=403)

    messages = messages_from_json(request.json['messages'])
    try:
        for message in messages:
            if message.body:
                print(message.from_user, ':', message.body)
                handle_secondary_message_types(message)
                # if handle_bot_names(message):
                #    break
                if isinstance(message, TextMessage):
                    response_picker(message)
    except (IndexError, AttributeError) as error:
        print("No messages found.", error)
    return Response(status=200)


def response_picker(message):
    data = message.body
    analysis_bayes = blobber(data)
    sentiment = analysis_bayes.sentiment
    subjectivity = analysis_bayes.subjectivity
    polarity = analysis_bayes.polarity
    sentiment_label = sentiment.classification
    print(sentiment)
    print(type(sentiment))
    accuracy = max(sentiment.p_pos, sentiment.p_neg)
    if polarity > 0:
        txt_polar = "Your tone is {}% Positive\n".format(polarity * 100)
    if polarity < 0:
        txt_polar = "Your tone is {}% Negative\n".format(polarity * 100)
    if polarity == 0:
        txt_polar = "Your tone is Neutral. Like a Machine.\n"
    if subjectivity > 0.80:
        txt_subj = "Your truth is very subjective.\n"
    elif subjectivity > 0.6:
        txt_subj = "Your truth is pretty subjective.\n"
    if subjectivity < 0.4:
        txt_subj = "Your truth is pretty objective.\n"
    if subjectivity < 0.2:
        txt_subj = "Your truth is very objective.\n"

    if sentiment_label == 'pos':
        sentiment_label = 'Positive Vibes!'
    if sentiment_label == 'neg':
        sentiment_label = 'Negative Vibes :('
    # send_messages(message, text_to_send=txt_polar + txt_subj)
    send_messages(message, text_to_send="Sentiment: {}\nSubjectivity: {}%\nAccuracy: {}%\nPolarity: {}%".format(
        sentiment_label, subjectivity * 100, round(accuracy, 2), round(polarity * 100, 0))


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
        send_messages(message, text_to_send="Hello and welcome")
        send_messages(message, text_to_send="This bot is your portal to unlimited knowledge, with the added side effect of pwning your friends when they start spewing about incorrect facts")
        send_messages(message, text_to_send="To use in a group conversation ping the bot with the keywords you want to use")
        send_messages(message, text_to_send="Ex: @agoogol Michaelangelo")
        send_messages(message, text_to_send="Ex: @agoogol 1001/1337")
        send_messages(message, text_to_send="Ex: @agoogol UN")


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

    post_url='https://www.googleapis.com/urlshortener/v1/url?key={}'.format(config["google_api_key"])
    payload={'longUrl': url}
    headers={'content-type': 'application/json'}
    r=requests.post(post_url, data=json.dumps(payload), headers=headers)
    # return only the relevant link
    return json.loads(r.text)["id"]


if __name__ == "__main__":
    raven_client=Client(config['sentry_hook'])
    app.run(host='0.0.0.0', port=int(config["port"]), debug=False)
