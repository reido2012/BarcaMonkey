import datetime
import os
import string
import pytz
import json

TZ = pytz.timezone('Europe/London')
DIRNAME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Sport888Event:
    def __init__(self, event_obj, date, course_name):
        self.url = f"https://www.888sport.com/horse-racing-betting/#/racing/event/{event_obj['id']}"
        self._set_event_attrs(event_obj, course_name)
        self.date = date

    def _set_event_attrs(self, event_obj, course_name):
        self.id = event_obj['id']
        self.time = event_obj['originalStartTime']
        self.location = str(course_name).lower()
        self.horse_odds = {}

    def get_url(self):
        return self.url

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
                    "url": "",
                    "horses": None
                },
                "oddschecker": {
                    "url": "",
                    "horses": None
                },
                "888Sport": {
                    "url": self.url,
                    "horses": self.horse_odds
                }
            }
            self._write_to_json(filepath, new_obj)

    def _modify_json(self, filepath):
        with open(filepath) as f:
            data = json.load(f)

        if data['888Sport']['horses']:
            self.update_odds_list(data)

        data['888Sport']['horses'] = self.horse_odds
        data['888Sport']['url'] = self.url

        self._write_to_json(filepath, data)

    def set_horses(self, horses):
        for horse in horses:
            horse_name = horse['englishLabel']
            horse_odds = float(horse['odds']) / 1000

            if horse_odds == -0.001:
                continue  # SP horse has no odds yet

            name = self.format_horse_name(horse_name)

            if name not in self.horse_odds.keys():
                self.horse_odds[name] = []

            current_time = datetime.datetime.now(TZ).strftime("%H:%M:%S")
            self.horse_odds[name].append((horse_odds, current_time))

    def update_odds_list(self, json_data):
        if 'horses' not in json_data['888Sport'].keys():
            return

        old_horse_odds = json_data['888Sport']['horses']

        for horse in self.horse_odds:
            if horse in old_horse_odds.keys():
                odds_horse = old_horse_odds[horse]
                self.horse_odds[horse] = odds_horse + self.horse_odds[horse]

    def _write_to_json(self, filepath, obj):
        with open(filepath, 'w') as f:
            json.dump(obj, f, indent=4)

    def __str__(self):
        return f"Location: {self.location} \n " \
               f"Date: {self.date} \n" \
               f"Time: {self.time} \n" \
               f"Horses: {self.horse_odds}\n " \
               f"URL: {self.url} "

    def format_horse_name(self, horse_name):
        translator = str.maketrans('', '', string.punctuation)
        horse_name = horse_name.lower()
        horse_name.translate(translator)
        return horse_name
