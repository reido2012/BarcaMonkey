import requests
import time
import xmltodict
import datetime
import os
import json
import string

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

    def __init__(self):
        self._XML_URL = "http://odds.smarkets.com/oddsfeed.xml"
        s1 = time.time()
        self.xml_dict = xmltodict.parse(requests.get(self._XML_URL).text)['odds']
        s2 = time.time()
        print(f"Time Taken: {s2 -s1}")
        self.date_time = datetime.datetime.now()
        if self.date_time.hour < 21:
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
                horses = event_obj['market'][0]['contract']
                sorted_horses = sorted(horses, key=lambda x: x['@slug'])
                new_event.set_horses(sorted_horses)
                new_event.send_to_json()

                print(new_event)

    # def print_horse_racing_tree(self):
    #     print(self.date_time)
    #
    #     for event_obj in self.xml_dict['event']:
    #         if event_obj['@type'] == 'Horse racing race' and event_obj['@date'] == self.current_date and event_obj['@state'] == 'upcoming':
    #             print("*" * 80)
    #             print(event_obj['@parent_name'])
    #             print(event_obj['@name'])
    #             print(event_obj['@date'])
    #             print(event_obj['@state'])
    #             print(event_obj['@url'])
    #             print("https://smarkets.com/event/" + event_obj['@id'] + event_obj['@url'])
    #             if not event_obj['market']:
    #                 continue
    #
    #             print(event_obj['market'][0]['@slug'])
    #             print("Name ----------------- Offers ------------------ Bids")
    #             horses = event_obj['market'][0]['contract']
    #             sorted_horses = sorted(horses, key=lambda x: x['@slug'])
    #
    #             for horse in sorted_horses:
    #                 name = horse['@name']
    #                 bids = horse['bids']
    #                 offers = horse['offers']
    #
    #                 if not bids and not offers:
    #                     print(f"{name} --- None  --- None")
    #
    #                 if bids:
    #                     if offers:
    #                         if bids['price'] and offers['price']:
    #                             self._print_horse_odds(name, bids['price'], offers['price'])
    #                     else:
    #                         if bids['price']:
    #                             self._print_horse_odds(name, bids, [])
    #
    #                 else:
    #                     if offers:
    #                         if offers['price']:
    #                             self._print_horse_odds(name, [], offers)
    #
    # def _print_horse_odds(self, name, bids, offers):
    #     offers = self._get_odds(offers)[::-1]
    #     bids = self._get_odds(bids)
    #     print(name)
    #     print(f"|{offers[0][0]}| |{offers[1][0]}| |{offers[2][0]}| -- |{bids[0][0]}| |{bids[1][0]}| |{bids[2][0]}|")
    #
    #     print(f"|£{offers[0][1]}| |£{offers[1][1]}| |£{offers[2][1]}| --- "
    #           f"|£{bids[0][1]}| |£{bids[1][1]}| |£{bids[2][1]})")

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

