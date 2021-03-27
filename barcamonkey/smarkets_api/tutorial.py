import logging
from logging.config import fileConfig
from pprint import pprint
import datetime
import client
import time
import dateparser
import json
import os
import string
import datetime
import pytz
from collections import OrderedDict
import pandas as pd

MAX_WORKERS = 4
TZ = pytz.timezone('Europe/London')
ODS_CHECKER_NEXT_DAY = 'https://www.oddschecker.com/football/'
DIRNAME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

df = pd.read_csv (str(DIRNAME)+"/TeamNameMapping.csv")
print(df)

class SmarketsEvent:
    def __init__(self, id, time, date, parent, state, type, url, teams, odds):
        self.id = id
        self.time = time
        self.date = date
        self.parent = parent
        self.state = state
        self.type = type
        self.url = url
        self.teams = teams
        self.odds = odds

    def send_to_json(self):
        folder_path = f"{DIRNAME}/events/{self.date}/"
        filename = f"{self.teams[0]}-{self.teams[1]}-{self.time}.json"
        filepath = folder_path + filename

        if os.path.isfile(filepath):
            self._modify_json(filepath)
        else:

            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            new_obj = {
                "smarkets": {
                    "url": self.url,
                    "horses": {self.teams[i]: self.odds[i] for i in range(len(self.teams))}
                },
                "oddschecker": {
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

        data['smarkets']['horses'] = {self.teams[i]: self.odds[i] for i in range(len(self.teams))}
        data['smarkets']['url'] = self.url

        self._write_to_json(filepath, data)

    def update_odds_list(self, json_data):
        if 'horses' not in json_data['smarkets'].keys():
            return

        old_odds = json_data['smarkets']['horses']

        for horse in self.odds:
            if horse in old_odds.keys():
                odds_horse = old_odds[horse]
                self.odds[horse] = odds_horse + self.odds[horse]

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

def run_scraper():
    print()

    import client
    fileConfig('logging.config', disable_existing_loggers=False)

    # instantiate client: single instance per session
    # copy the template from configuration_template.toml and fill it with
    # your credentials!
    client = client.SmarketsClient()

    # do initial authentication
    client.init_session()

    # pick some market and contract
    # market_id = '7289490'
    # contract_id = '24174814'

    # get some events
    events = client.get_available_events(['upcoming'], ['football_match'], datetime.date(2999, 1, 1), 1)
    for event in events:
        time.sleep(2)

        home = event["name"][0:event["name"].find("vs")-1].lower()
        away = event["name"][event["name"].find("vs")+3:].lower()
        print(home)
        print(away)
        # teams = [home, away, "draw"]
        # date0 = event["start_date"].split("-")
        # date1 = date0[2] + "-" + datetime.date(1900, int(date0[1]), 1).strftime('%B') + "-" + date0[0]
        # time0 = event["start_datetime"]
        # time1 = time0[11:13] + ":" + time0[14:16]
        # market = client.get_related_markets([event])
        # quote = client.get_quotes([market[0]["id"]])
        # keys = ' '.join(quote.keys()).split(" ")
        # id = event["id"]
        # type = event["type"]
        # url = "smarkets.com/event/" + id
        #
        # odds = [None, None, None]
        # for i in range(0, 3):
        #     odds[i] = round(10000 / quote[keys[i]]["bids"][0]["price"], 2)
        #
        # match = SmarketsEvent(id, time1, date1, "parent", "state", type, url, teams, odds)
        # match.send_to_json()



    # place some bets

    # client.place_order(
    #     market_id,    # market id
    #     contract_id,  # contract id
    #     50,           # percentage price * 10**4, here: 0.5% / 200 decimal / 19900 american
    #     500000,       # quantity: total stake * 10**4, here: 50 GBP. Your buy order locks 0.25 GBP, as
    #                   #      0.25 GBP * 200 = 50 GBP
    #     'buy',        # order side: buy or sell
    # )


    # lets get the orders now!
    # pprint(client.get_orders(states=['created', 'filled', 'partial']))
    #
    # pprint(client.get_accounts())

    # eeh, changed my mind
    # client.cancel_order('202547466272702478')


if __name__ == '__main__':
    run_scraper()
    print()
