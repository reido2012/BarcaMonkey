import os
import glob
import json
import datetime
import pytz

TZ = pytz.timezone('Europe/London')

class Monkey:
    def __init__(self):
        self.events_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/events/"

    def has_event_passed(self, filepath):
        split_filepath = filepath.split("/")
        file_name_time = split_filepath[-1:][0].split("-")[0].split(":")
        year, month, day = split_filepath[-2:-1][0].split("-")
        now = datetime.datetime.now(TZ)
        file_time = now.replace(year=int(year), day=int(day), month=int(month), hour=int(file_name_time[0]), minute=int(file_name_time[1]))
        return now > file_time

    def compare_events(self, date_to_check):
        folder_path = self.events_path + str(date_to_check)
        results = []
        for filepath in glob.glob(folder_path + "/*.json"):
            with open(filepath) as f:
                data = json.load(f)

            smarkets_event_json = data['smarkets']
            smarkets_url = smarkets_event_json['url']

            oddschecker_event_json = data['oddschecker']

            if self.has_event_passed(filepath):
                continue

            if 'horses' not in oddschecker_event_json.keys():
                continue

            if 'horses' not in smarkets_event_json.keys():
                continue

            if not oddschecker_event_json['horses']:
                continue

            if not smarkets_event_json['horses']:
                continue

            oddschecker_horses = oddschecker_event_json['horses']
            oddschecker_url = oddschecker_event_json['url']

            event_results = {}
            for smarkets_horse, smarkets_horse_info in smarkets_event_json['horses'].items():

                if not smarkets_horse_info:
                    continue

                smarkets_horse_odds, smarket_horse_lay, harvest_time = smarkets_horse_info[-1:][0]

                if not smarkets_horse_odds: #Odds
                    continue
                if smarkets_horse not in oddschecker_horses.keys():
                    continue

                smarkets_horse_odds = float(smarkets_horse_odds)

                for oddschecker_bookie, bookie_odds_list in oddschecker_horses[smarkets_horse].items():
                    # print(f"Bookie Odds List: {bookie_odds_list}")
                    if not bookie_odds_list:
                        continue

                    bookie_odds, oc_harvest_time = bookie_odds_list[-1:][0]

                    if not bookie_odds:
                        continue

                    bookie_odds = float(bookie_odds)
                    difference = round(abs(smarkets_horse_odds - bookie_odds), 4)
                    if smarkets_horse_odds < bookie_odds:
                        event_results[smarkets_horse] = {}
                        event_results[smarkets_horse][oddschecker_bookie] = {
                            'diff': difference,
                            'smarkets': smarkets_horse_odds,
                            'lay': "£" + smarket_horse_lay,
                            'odds_checker': bookie_odds,
                            'time_scraped_smarkets': harvest_time,
                            'time_scraped_oc': oc_harvest_time
                        }
            if event_results:
                result = (smarkets_url, oddschecker_url, event_results)
                results.append(result)

        return results



