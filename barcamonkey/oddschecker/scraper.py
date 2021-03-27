import dateparser
import json
import os
import string
import datetime
import pytz
from datetime import date
from concurrent import futures
from core_utils import get_soup
from bookie_codes import BOOKIE_CODES_AND_INDICES

MAX_WORKERS = 4
TZ = pytz.timezone('Europe/London')
ODS_CHECKER_NEXT_DAY = 'https://www.oddschecker.com/football/'
DIRNAME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Event:

    def __init__(self, url, title, event_name, home, away, time):
        self.url = f"https://www.oddschecker.com{url}"
        self.date = None
        self.time = time
        self.title = title
        self.event_name = event_name
        self.home = home
        self.away = away
        self.odds = {}
        self.country = None
        self.league = None

    def get_url(self):
        return self.url

    def parse_time(self):
        return dateparser.parse(self.data_time)

    def send_to_json(self):
        folder_path = f"{DIRNAME}/events/"+self.date+"/"
        filename = f"{self.home}-{self.away}-{self.time}.json"
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
                    "url": self.url,
                    "horses": self.odds
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

        if data['oddschecker']['horses']:
            self.update_odds_list(data)

        data['oddschecker']['horses'] = self.odds
        data['oddschecker']['url'] = self.url

        self._write_to_json(filepath, data)

    def update_odds_list(self, json_data):
        if 'horses' not in json_data['oddschecker'].keys():
            return

        old_horse_odds = json_data['oddschecker']['horses']

        for horse in self.odds.keys():
            for index, bookie_name in list(BOOKIE_CODES_AND_INDICES.values()):
                if horse in old_horse_odds.keys() and bookie_name in old_horse_odds[horse].keys():
                    odds_horse = old_horse_odds[horse][bookie_name]

                    if bookie_name not in self.odds[horse].keys():
                        continue

                    self.odds[horse][bookie_name] = odds_horse + self.odds[horse][bookie_name]

    def _write_to_json(self, filepath, obj):

        with open(filepath, 'w') as f:
            json.dump(obj, f, indent=4)

    def __str__(self):
        return f"Title: {self.title}\n " \
               f"Time: {self.time} \n" \
               f"URL: {self.url} "


def run_scraper(country, league, current_day_limit=21):
    # Every morning
    # Get links for the events of the day
    soup = get_soup(ODS_CHECKER_NEXT_DAY+country+league)

    # Location - Times
    match_details = get_tags_by_attr(soup, 'tr', 'class', 'match-on')
    # only include matches that haven't started yet

    days_events = [item for sublist in list(map(create_events, match_details)) for item in sublist]
    if days_events:
        updated_events = do_concurrently(get_odds_from_event_table, days_events)

        for event in list(updated_events):
            if event:
                event.send_to_json()


def get_odds_from_event_table(event):
    if '/abandoned-' in event.url:
        return None

    soup = get_soup(event.url)

    date0 = get_tag_by_attr(soup, 'span', 'class', 'date')
    date1 = date0.contents[0]
    date2 = date1.split()
    date3 = date2[1][:-2] + "-" + date2[2] + "-" + date.today().strftime("%Y")
    event.date = date3

    odds_table = get_tag_by_attr(soup, 'tbody', 'id', 't1')

    if not odds_table:
        return None

    match_rows = odds_table.find_all('tr')

    for match_row in match_rows:
        if not match_row:
            continue

        team_name = match_row['data-bname']
        team_name = format_horse_name(team_name)

        our_odds = {}
        all_odds = match_row.find_all('td')

        # all_odds_len = len(all_odds)
        for index, name in list(BOOKIE_CODES_AND_INDICES.values()):
            index += 2
            team_odd = all_odds[index]['data-odig']
            current_time = datetime.datetime.now(TZ).strftime("%H:%M:%S")

            if name not in our_odds.keys():
                our_odds[name] = []

            if team_odd == "0":
                our_odds[name].append((None, current_time))
            else:
                our_odds[name].append((team_odd, current_time))

            # if non_runner:
            #     our_odds[name].append((None, current_time))

        event.odds[team_name] = our_odds
    return event
    # Could avoid double checking by saving the last data-bid value of tr


def create_events(match_detail):
    events = []
    event = parse_event(match_detail)
    if event.time:
        events.append(event)

    return events


def parse_event(match_detail):
    match_tag = match_detail.find('a', {'class': 'beta-callout full-height-link whole-row-link'})

    match_href = match_tag['href']
    match_title = match_tag['title']
    match_event_name = match_tag['data-event-name']

    match_home = get_tags_by_attr(match_detail, 'p', 'class', 'fixtures-bet-name')[0].contents[-1]
    match_away = get_tags_by_attr(match_detail, 'p', 'class', 'fixtures-bet-name')[1].contents[-1]
    match_time = get_tag_by_attr(match_detail, 'span', 'class', 'time-digits').contents[0]
    print(match_home)
    print(match_away)
    return Event(match_href, match_title, match_event_name, match_home, match_away, match_time)


def do_concurrently(a_function, a_list):
    workers = min(MAX_WORKERS, len(a_list))
    with futures.ThreadPoolExecutor(workers) as executor:
        res = executor.map(a_function, a_list)
    return res


def get_tags_by_attr(soup, tag, attr, value):
    return soup.findAll(tag, {attr: value.split(" ")})


def get_tag_by_attr(soup, tag, attr, value):
    return soup.find(tag, {attr: value.split(" ")})


def format_horse_name(horse_name):
    translator = str.maketrans('', '', string.punctuation)
    horse_name = horse_name.lower()
    horse_name.translate(translator)
    return horse_name


if __name__ == '__main__':
    print()
    print()
    print()
    print()
    print()
    print()
    print()
    print()
    print()
    print()
    print()
    print()
    print()
    print()
    print()
    run_scraper("ENGLISH/", "PREMIER-LEAGUE/")
    run_scraper("ENGLISH/", "CHAMPIONSHIP/")
    run_scraper("ENGLISH/", "LEAGUE-1/")
    run_scraper("ENGLISH/", "LEAGUE-2/")
    run_scraper("ENGLISH/", "FA-CUP/")
    run_scraper("ENGLISH/", "EFL-CUP/")
    # run_scraper("SCOTTISH", "PREMIERSHIP/")
    run_scraper("SPAIN/", "LA-LIGA-PRIMERA/")
    run_scraper("GERMANY/", "BUNDESLIGA/")
    run_scraper("ITALY/", "SERIE-A/")
    run_scraper("FRANCE/", "LIGUE-1/")
    run_scraper("SPAIN/", "LA-LIGA-PRIMERA/")
    run_scraper("CHAMPIONS-LEAGUE", "/")
    run_scraper("EUROPA-LEAGUE", "/")
    print("SUCCESS")



