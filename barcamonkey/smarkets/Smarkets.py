import requests
import time
import xmltodict
import datetime
import os
import json
import string
import sys
import gzip

from collections import OrderedDict
DIRNAME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Event:
    def __init__(self, event_obj, date):
        self._set_event_attrs(event_obj)
        self.date = date

    def _set_event_attrs(self, event_obj):
        self.id = event_obj['@id']
        self.time = event_obj['@name']
        self.parent = event_obj['@parent']
        self.location = str(event_obj['@parent_name']).lower()
        self.state = event_obj['@state']
        self.url = "https://smarkets.com/event/" + self.id + event_obj['@url']
        self.type = event_obj['@type']
        self.horse_odds = {}

    def set_horses(self, horses):
        for horse in horses:
            name = horse['@name']
            name = format_horse_name(name)

            bids = horse['bids']
            self.horse_odds[name] = (None, None)

            if bids and bids['price']:
                bids = get_odds(bids['price'])
                self.horse_odds[name] = bids[0]

    def send_to_json(self):
        folder_path = f"{DIRNAME}/events/{self.date}/"
        filename = f"{self.time}-{self.location}.json"
        filepath = folder_path + filename

        if os.path.isfile(filepath):
            self._modify_json(filepath)
        else:

            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            new_obj = {
                "smarkets":{
                    "url": self.url,
                    "horses": self.horse_odds
                },
                "oddschecker":{}
            }
            self._write_to_json(filepath, new_obj)

    def _modify_json(self, filepath):
        with open(filepath) as f:
            data = json.load(f)

        data['smarkets']['horses'] = self.horse_odds
        data['smarkets']['url'] = self.url

        self._write_to_json(filepath, data)

    def _write_to_json(self, filepath, obj):

        with open(filepath, 'w') as f:
            json.dump(obj, f, indent=4)

    def __str__(self):
        return f"Event Name: {self.location} \n " \
               f"Date Time: {self.time} " \
               f"\n URL: {self.url} "


class SmarketsParser:
    """
    Handles downloading and parsing of the Smarkets XML odds feed

    The XML feed is updated every few seconds but the information is delayed by 30 seconds.
    """

    #Date Format
    #YEAR - MONTH - DAY

    def __init__(self, current_day_limit=21):
        self._XML_URL = "http://odds.smarkets.com/oddsfeed.xml.gz"
        filename = self._XML_URL.split("/")[-1]
        with open(filename, "wb") as f:
            r = requests.get(self._XML_URL)
            f.write(r.content)

        with requests.get(self._XML_URL) as r:
            print(f"Status Code: {r.status_code}")
            print(f"Encoding:{r.encoding}")
            # r.encoding = 'utf-8'
            # print(r.content.decode('utf-8'))
            self.xml_dict = xmltodict.parse(gzip.GzipFile(filename))['odds']
            self.date_time = datetime.datetime.now()
            if self.date_time.hour < current_day_limit:
                self.current_date = str(self.date_time.year) + "-" + '{:02d}'.format(self.date_time.month) + "-" + '{:02d}'.format(self.date_time.day)
            else:
                self.current_date = str(self.date_time.year) + "-" + '{:02d}'.format(
                    self.date_time.month) + "-" + '{:02d}'.format(self.date_time.day + 1)

    def write_or_update_events(self):
        for event_obj in self.xml_dict['event']:
            if event_obj['@type'] == 'Horse racing race' and event_obj['@date'] == self.current_date:

                if not event_obj['market']:
                    continue

                new_event = Event(event_obj, self.current_date)

                if type(event_obj['market']) == OrderedDict:
                    horses = event_obj['market']['contract']
                else:
                    horses = event_obj['market'][0]['contract']

                sorted_horses = sorted(horses, key=lambda x: x['@slug'])
                new_event.set_horses(sorted_horses)
                new_event.send_to_json()

        print("Finished Handling Smarkets")

    def _get_odds(self, odds_list):
        results_list = []

        if len(odds_list) == 0 or not odds_list:
            return [(None, 0), (None, 0), (None, 0)]

        if type(odds_list) == OrderedDict:
            if '@decimal' in odds_list.keys():
                results_list.append((odds_list['@decimal'], odds_list['@backers_stake']))
            else:
                return [(None, 0), (None, 0), (None, 0)]
        else:
            for i in range(len(odds_list)):
                if '@decimal' in odds_list[i].keys():
                    results_list.append((odds_list[i]['@decimal'], odds_list[i]['@backers_stake']))

        if len(results_list) < 3:
            [results_list.append((None, 0)) for _ in range(3 - len(results_list))]

        return results_list


def get_odds(odds_list):
    results_list = []

    if len(odds_list) == 0 or not odds_list:
        return [(None, 0), (None, 0), (None, 0)]

    if type(odds_list) == OrderedDict:
        if '@decimal' in odds_list.keys():
            results_list.append((odds_list['@decimal'], odds_list['@backers_stake']))
        else:
            return [(None, 0), (None, 0), (None, 0)]
    else:
        for i in range(len(odds_list)):
            if '@decimal' in odds_list[i].keys():
                results_list.append((odds_list[i]['@decimal'], odds_list[i]['@backers_stake']))

    if len(results_list) < 3:
        [results_list.append((None, 0)) for _ in range(3 - len(results_list))]

    return results_list


def format_horse_name(horse_name):
    translator = str.maketrans('', '', string.punctuation)
    horse_name = horse_name.lower()
    horse_name.translate(translator)
    return horse_name

