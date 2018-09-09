import string
from twilio.rest import Client
import os


def format_horse_name(horse_name):
    translator = str.maketrans('', '', string.punctuation)
    horse_name = horse_name.lower().replace(" ", "")
    horse_name.translate(translator)
    print(horse_name)
    return horse_name


