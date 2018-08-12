import requests
import time
import xmltodict

from collections import OrderedDict


class Event:
    def __init__(self, event_obj, date):
        self._set_event_attrs(event_obj)
        self.date = date

    def _set_event_attrs(self, event_obj):
        self.id = event_obj['@id']
        self.name = event_obj['@name']
        self.parent = event_obj['@parent']
        self.parent_name = event_obj['@parent_name']
        self.state = event_obj['@state']
        self.time = event_obj['@time']
        self.url = event_obj['@url']
        self.type = event_obj['@type']


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

    def print_horse_racing_tree(self):
        for event_obj in self.xml_dict['event']:
            if event_obj['@type'] == 'Horse racing race' and event_obj['@date'] == "2018-08-13":
                print("*" * 80)
                print(event_obj['@parent_name'])
                print(event_obj['@name'])
                print(event_obj['@date'])

                print(event_obj['market'][0]['@slug'])
                print("Name ----------------- Offers ------------------ Bids")
                horses = event_obj['market'][0]['contract']
                sorted_horses = sorted(horses, key=lambda x: x['@slug'])

                for horse in sorted_horses:
                    name = horse['@name']
                    bids = horse['bids']
                    offers = horse['offers']

                    if not bids and not offers:
                        print(f"{name} --- None  --- None")

                    if bids:
                        if offers:
                            if bids['price'] and offers['price']:
                                self._print_horse_odds(name, bids['price'], offers['price'])
                        else:
                            if bids['price']:
                                self._print_horse_odds(name, bids, [])

                    else:
                        if offers:
                            if offers['price']:
                                self._print_horse_odds(name, [], offers)

    def _print_horse_odds(self, name, bids, offers):
        offers = self._get_odds(offers)[::-1]
        bids = self._get_odds(bids)
        print(name)
        print(f"|{offers[0][0]}| |{offers[1][0]}| |{offers[2][0]}| -- |{bids[0][0]}| |{bids[1][0]}| |{bids[2][0]}|")

        print(f"|£{offers[0][1]}| |£{offers[1][1]}| |£{offers[2][1]}| --- "
              f"|£{bids[0][1]}| |£{bids[1][1]}| |£{bids[2][1]})")

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





