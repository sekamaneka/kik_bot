"""Return duckduckgo search results to the kik users."""

import urllib
import json
import os
import sys
import requests

from flask import request, Response
from kik import Configuration
from kik.messages import messages_from_json, TextMessage, StartChattingMessage, ScanDataMessage, StickerMessage, VideoMessage, PictureMessage, LinkMessage
from raven import Client

parentPath = os.path.abspath("..")
if parentPath not in sys.path:
    sys.path.insert(0, parentPath)
import utility


@utility.app.route('/', methods=['POST'])
def incoming():
    """Handle incoming traffic."""
    if not utility.kik.verify_signature(request.headers.get('X-Kik-Signature'), request.get_data()):
        return Response(status=403)

    messages = messages_from_json(request.json['messages'])
    try:
        for message in messages:
            if message.body:
                print(message.from_user, ':', message.body)
                utility.handle_secondary_message_types(message)
                # if handle_bot_names(message):
                #    break
                if isinstance(message, TextMessage):
                    response_picker(message)
    except (IndexError, AttributeError) as error:
        print("No messages found.", error)
    return Response(status=200)


def response_picker(message):
    """Handle duckduckgo api."""

    base = "http://api.duckduckgo.com/?q="
    args = "&format=json&no_html=1&no_redirect=1&t=b4d4b00mb4d4b00m"
    string = base + urllib.parse.quote(message.body) + args
    data = requests.get(string).text
    dict_of_data = json.loads(data)
    # print(string)
    # for i,j in dict_of_data.items():
    #   print(i,j)
    rtype = dict_of_data["Type"]
    # print(message.body)
    if rtype == 'D':
        dissambiguation_t(message, dict_of_data)
    elif rtype == 'A':
        article_t(message, dict_of_data)
    elif rtype == 'C':
        pass
    elif rtype == 'N':
        instant_text = "This is a regular, real or imaginary person. Finding information about them should be harder than this."
        utility.send_messages(message, "", instant_text, 0)
    elif rtype == 'E':
        exclusive_t(message, dict_of_data, args, string)
    else:
        instant_url = "https://safe.duckduckgo.com/?q=" + urllib.parse.quote(message.body)
        utility.send_messages(message, instant_url, message.body, "https://computerbeast.files.wordpress.com/2010/08/duck-duck-go.png", 1)


def dissambiguation_t(message, dict_of_data):
    """Handle dissambiguation type answer."""

    data = dict_of_data["RelatedTopics"][0]
    instant_text = data["Text"]
    instant_url = data["FirstURL"]
    instant_pic = data["Icon"]["URL"]
    utility.send_messages(message, instant_url, instant_text, instant_pic, 1)


def article_t(message, dict_of_data):
    """Handle article type answer."""

    instant_text = dict_of_data["Abstract"]
    instant_url = dict_of_data["AbstractURL"]
    instant_pic = dict_of_data["Image"]
    utility.send_messages(message, instant_url, instant_text, instant_pic, 1)


def exclusive_t(message, dict_of_data, args, string):
    """Handle exclusive types. There are a lot of subtypes."""

    atype = dict_of_data["AnswerType"]
    redirect = dict_of_data["Redirect"]
    print(atype)
    if atype == 'calc':
        utility.send_messages(message, inc_url=string[:-len(args)], text_to_send=message.body, link=1, inc_title="Calculator")
    elif redirect:
        a = message.body.split()
        # inc_title = a[0]
        text_to_send = " ".join([i for i in a[1:]])
        utility.send_messages(message, inc_url=redirect, link=1, text_to_send=text_to_send, instant_pic="https://computerbeast.files.wordpress.com/2010/08/duck-duck-go.png")
    else:
        instant_text = dict_of_data["Answer"]
        utility.send_messages(message, text_to_send=instant_text)


utility.run()
