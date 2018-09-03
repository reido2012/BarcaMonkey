import os
import glob
import json
import datetime

class Monkey:
    def __init__(self):
        self.events_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/events/"

    def has_event_passed(self, filepath):
        file_name_time = filepath.split("/")[-1:][0].split("-")[0].split(":")
        now = datetime.datetime.now()
        file_time = now.replace(hour=int(file_name_time[0]), minute=int(file_name_time[1]))
        return now > file_time

    def compare_events(self, date_to_check):
        folder_path = self.events_path + str(date_to_check)
        results = []
        for filepath in glob.glob(folder_path + "/*.json"):
            #print(f"Filepath: {filepath}")

            with open(filepath) as f:
                data = json.load(f)


            smarkets_event_json = data['smarkets']
            smarkets_url = smarkets_event_json['url']

            oddschecker_event_json = data['oddschecker']

            if self.has_event_passed(filepath):
                continue

            if 'horses' not in oddschecker_event_json.keys():
                continue

            if 'horses' not in oddschecker_event_json.keys():
                continue

            oddschecker_horses = oddschecker_event_json['horses']
            oddschecker_url = oddschecker_event_json['url']

            event_results = {}
            for smarkets_horse, smarkets_horse_info in smarkets_event_json['horses'].items():
                smarkets_horse_odds, smarket_horse_lay = smarkets_horse_info

                if not smarkets_horse_odds: #Odds
                    continue
                if smarkets_horse not in oddschecker_horses.keys():
                    continue

                smarkets_horse_odds = float(smarkets_horse_odds)

                for oddschecker_bookie, bookie_odds in oddschecker_horses[smarkets_horse].items():
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
                            'odds_checker': bookie_odds
                        }
            if event_results:
                print(f"Smarkets URL: {smarkets_url}")
                print(f"Odds Checker URL: {oddschecker_url}")
                print(event_results)
                result = (smarkets_url, oddschecker_url, event_results)

                results.append(result)
                print("*" * 40)

        return results



