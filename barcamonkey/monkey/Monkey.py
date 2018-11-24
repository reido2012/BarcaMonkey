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
        file_time = now.replace(year=int(year), day=int(day), month=int(month), hour=int(file_name_time[0]),
                                minute=int(file_name_time[1]))
        return now > file_time

    def is_event_too_close(self, filepath, margin=15):
        margin = datetime.timedelta(minutes=margin)
        split_path = filepath.split("/")
        race_date = split_path[-2:-1][0]
        race_time = split_path[-1:][0].split("-")[0]
        race_dt = datetime.datetime.strptime(f"{race_date} {race_time}", "%Y-%m-%d %H:%M").replace(tzinfo=TZ)
        now = datetime.datetime.now(TZ)

        return race_dt <= now + margin

    def qualifying_bet_profit(self, smarkets_odd, odds_checker):
        return round((0.98 * ((10 * odds_checker) / smarkets_odd - 0.02) - 10), 2)

    def free_bet_profit(self, smarkets_odd, odds_checker):
        return round(((10 * (odds_checker - 1)) / (smarkets_odd - 0.02)), 2)

    def compare_events(self, date_to_check):
        folder_path = self.events_path + str(date_to_check)
        results = []
        for filepath in glob.glob(folder_path + "/*.json"):

            if self.has_event_passed(filepath):
                print(f"Event Has Passed: {filepath}")
                continue

            if self.is_event_too_close(filepath):
                print(f"Event Too Close: {filepath}")
                continue

            with open(filepath) as f:
                data = json.load(f)

            smarkets_event_json = data['smarkets']
            smarkets_url = smarkets_event_json['url']

            oddschecker_event_json = data['oddschecker']

            sport888_event_json = data['888Sport']

            if 'horses' not in oddschecker_event_json.keys():
                continue

            if 'horses' not in smarkets_event_json.keys():
                continue

            if 'horses' not in sport888_event_json.keys():
                continue

            if not oddschecker_event_json['horses']:
                continue

            if not smarkets_event_json['horses']:
                continue

            if not sport888_event_json['horses']:
                continue

            oddschecker_horses = oddschecker_event_json['horses']
            sport888_horses = sport888_event_json['horses']

            oddschecker_url = oddschecker_event_json['url']

            event_results = {}
            for smarkets_horse, smarkets_horse_info in smarkets_event_json['horses'].items():

                oddschecker_available = True
                sport888_available = True

                if not smarkets_horse_info:
                    continue

                smarkets_horse_odds, smarket_horse_lay, harvest_time = smarkets_horse_info[-1:][0]

                if not smarkets_horse_odds:  # Odds
                    continue

                if smarkets_horse not in oddschecker_horses.keys():
                    oddschecker_available = False

                if smarkets_horse not in sport888_horses.keys():
                    sport888_available = False

                if (not sport888_available) and (not oddschecker_available):
                    continue

                smarkets_horse_odds = float(smarkets_horse_odds)

                event_results[smarkets_horse] = {}

                if sport888_available:
                    sport888_horse_odds, harvest_time_888 = sport888_horses[smarkets_horse][-1:][0]

                    event_result_888 = self.create_event_result(smarkets_horse_odds, smarket_horse_lay, harvest_time, sport888_horse_odds, harvest_time_888, '888Sport')

                    if event_result_888:
                        event_results[smarkets_horse]['888Sport'] = event_result_888

                if oddschecker_available:
                    for oddschecker_bookie, bookie_odds_list in oddschecker_horses[smarkets_horse].items():
                        if not bookie_odds_list:
                            continue

                        bookie_odds, oc_harvest_time = bookie_odds_list[-1:][0]

                        event_result = self.create_event_result(smarkets_horse_odds, smarket_horse_lay, harvest_time,
                                                                bookie_odds, oc_harvest_time, oddschecker_bookie)

                        if event_result:
                            event_results[smarkets_horse][oddschecker_bookie] = event_result

            # Remove empty horses
            event_results = {smarkets_horse: info for smarkets_horse, info in event_results.items() if len(info) > 0}

            if event_results:
                result = (smarkets_url, oddschecker_url, event_results)
                results.append(result)

        return results

    def create_event_result(self, smarkets_odds, smarket_horse_lay, harvest_time_smarkets, bookie_odds,
                            harvest_time_bookie, bookie_name):

        if not bookie_odds:
            return None

        bookie_odds = float(bookie_odds)
        smarkets_odds = float(smarkets_odds)

        if smarkets_odds < bookie_odds:

            difference = round(abs(smarkets_odds - bookie_odds), 4)
            qb_profit = self.qualifying_bet_profit(smarkets_odds, bookie_odds)
            fb_profit = self.free_bet_profit(smarkets_odds, bookie_odds)
            high_qb = True if qb_profit >= 3.0 else False
            med_qb = True if 1.0 <= qb_profit < 3.0 else False
            min_qb_profit = 0.5
            min_fb_profit = 10

            if bookie_name in ['10 Bet', 'UNIBET']:
                min_qb_profit = -0.5

            if (qb_profit > min_qb_profit) or (fb_profit >= min_fb_profit):
                return {
                    'diff': difference,
                    'smarkets': smarkets_odds,
                    'lay': "£" + smarket_horse_lay,
                    'odds_checker': bookie_odds,
                    'time_scraped_smarkets': harvest_time_smarkets,
                    'time_scraped_oc': harvest_time_bookie,
                    'qb_profit': qb_profit,
                    'fb_profit': fb_profit,
                    'high_qb': high_qb,
                    'med_qb': med_qb
                }

        return None
