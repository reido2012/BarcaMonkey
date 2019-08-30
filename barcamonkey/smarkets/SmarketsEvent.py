import os
import json
import string
import pytz
import datetime

from collections import OrderedDict

TZ = pytz.timezone('Europe/London')
DIRNAME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class SmarketsEvent:
    def __init__(self, event_obj):
        self._set_event_attrs(event_obj)

    def _set_event_attrs(self, event_obj):
        self.id = event_obj['id']
        self.time = event_obj['time']
        self.parent = event_obj['parent']
        self.location = event_obj['location']
        self.state = event_obj['state']
        self.url = event_obj['url']
        self.type = event_obj['type']
        self.date = event_obj.date
        self.horse_odds = {}
        self.horse_info = {}

    def create_horse_odds(self, contracts, quotes):

        for contract in contracts:
            if contract['contract_type']['name'] != "NAMED_COMPETITOR":
                continue

            horse_id = contract['id']
            horse_name = contract['contract_type']['param']
            horse_info = contract['info']
            horse_info['state_or_outcome'] = contract['state_or_outcome']

            horse_odds = quotes[horse_id]
            curr_time = datetime.datetime.now(TZ).strftime("%H:%M:%S")
            horse_odds['time'] = curr_time

            if horse_name not in self.horse_odds.keys():
                self.horse_odds[horse_name] = []

            if horse_name not in self.horse_odds.keys():
                self.horse_info[horse_name] = horse_info

            self.horse_odds[horse_name].append(horse_odds)


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
                "smarkets": {
                    "url": self.url,
                    "horses": self.horse_odds
                },
                "oddschecker": {
                    "url": "",
                    "horses": None
                },

                "888Sport": {
                    "url": "",
                    "horses": None
                },

            }
            self._write_to_json(filepath, new_obj)

    def _modify_json(self, filepath):
        with open(filepath) as f:
            data = json.load(f)

        if data['smarkets']['horses']:
            self.update_odds_list(data)

        data['smarkets']['horses'] = self.horse_odds
        data['smarkets']['url'] = self.url

        self._write_to_json(filepath, data)

    def update_odds_list(self, json_data):
        if 'horses' not in json_data['smarkets'].keys():
            return

        old_horse_odds = json_data['smarkets']['horses']

        for horse in self.horse_odds:
            if horse in old_horse_odds.keys():
                odds_horse = old_horse_odds[horse]
                self.horse_odds[horse] = odds_horse + self.horse_odds[horse]

    def _write_to_json(self, filepath, obj):

        with open(filepath, 'w') as f:
            json.dump(obj, f, indent=4)

    def __str__(self):
        return f"Event Name: {self.location} \n " \
               f"Date Time: {self.time} " \
               f"\n URL: {self.url} "

    def _format_horse_name(self, horse_name):
        translator = str.maketrans('', '', string.punctuation)
        horse_name = horse_name.lower()
        horse_name.translate(translator)
        return horse_name

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
