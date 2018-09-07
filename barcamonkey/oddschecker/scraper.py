import dateparser
import json
import os
import string
import datetime
import pytz
from concurrent import futures
from .core_utils import get_soup
from .bookie_codes import BOOKIE_CODES_AND_INDICES

MAX_WORKERS = 4
TZ = pytz.timezone('Europe/London')
ODS_CHECKER_NEXT_DAY = 'https://www.oddschecker.com/horse-racing'
DIRNAME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Event:

    def __init__(self, url, data_time, title):
        self.url = f"https://www.oddschecker.com{url}"
        self.data_time = data_time
        self.title = title
        self.date_obj = self.parse_time()
        self.date = str(self.date_obj.year) + "-" + '{:02d}'.format(self.date_obj.month) + "-" + '{:02d}'.format(
            self.date_obj.day)
        self.time = '{:02d}'.format(self.date_obj.hour) + ":" + '{:02d}'.format(
            self.date_obj.minute)
        self.location = None
        self.horse_odds = {}

    def get_url(self):
        return self.url

    def parse_time(self):
        return dateparser.parse(self.data_time)

    def set_location(self, location):
        self.location = str(location).lower()

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
                    "url": "",
                    "horses": None
                },
                "oddschecker": {
                    "url": self.url,
                    "horses": self.horse_odds
                }
            }
            self._write_to_json(filepath, new_obj)

    def _modify_json(self, filepath):
        with open(filepath) as f:
            data = json.load(f)

        data['oddschecker']['horses'] = self.horse_odds
        data['oddschecker']['url'] = self.url

        self._write_to_json(filepath, data)

    def _write_to_json(self, filepath, obj):

        with open(filepath, 'w') as f:
            json.dump(obj, f, indent=4)

    def __str__(self):
        return f"Location: {self.location} \n " \
               f"Title: {self.title}\n " \
               f"Date: {self.date} \n" \
               f"Time: {self.time} \n" \
               f"Horses: {self.horse_odds}\n " \
               f"URL: {self.url} "


def run_scraper(current_day_limit=21):
    #Every morning
    #Get links for the events of the day
    soup = get_soup(ODS_CHECKER_NEXT_DAY)
    if datetime.datetime.now(TZ).hour < current_day_limit:
        race_meets_table = get_tag_by_attr(soup, 'div', 'class', 'race-meets')
    else:
        race_meets_table = get_tags_by_attr(soup, 'div', 'class', 'race-meets')[1]

    #Location - Times
    race_details = get_tags_by_attr(race_meets_table, 'div', 'class', 'race-details')
    days_events = [item for sublist in list(map(create_events, race_details)) for item in sublist]

    if days_events:
        updated_events = do_concurrently(get_odds_from_event_table, days_events)

        for event in list(updated_events):
            event.send_to_json()
    print("Finished Running Scraper")

def get_odds_from_event_table(event):
    #for event in events:
        #Every 30 seconds do this
    soup = get_soup(event.url)
    odds_table = get_tag_by_attr(soup, 'tbody', 'id', 't1')
    horse_rows = odds_table.find_all('tr')

    for horse_row in horse_rows:
        horse_name = horse_row['data-bname']
        horse_name = format_horse_name(horse_name)

        our_odds = {}
        all_odds = get_tags_by_attr(horse_row, 'td', 'class', 'bc bs')
        all_odds_len = len(all_odds)
        for index, name in list(BOOKIE_CODES_AND_INDICES.values()):
            if index >= all_odds_len:
                continue

            horse_odd = all_odds[index]['data-odig']
            if horse_odd == "0":
                our_odds[name] = None
            else:
                our_odds[name] = horse_odd

        event.horse_odds[horse_name] = our_odds

    return event
    # Could avoid double checking by saving the last data-bid value of tr


def create_events(race_detail):
    location = get_tag_by_attr(race_detail, 'a', 'class', 'venue beta-caption1').contents[0]

    race_times = get_tags_by_attr(race_detail, 'div', 'class', 'racing-time')
    events = []
    for race_time in race_times:
        if race_time:
            event = parse_event(race_time)
            if not event:
                continue

            event.set_location(location)
            events.append(event)

    return events


def parse_event(race_time):
    racing_tag = race_time.find('a', {'class': 'beta-footnote race-time time'})
    if not racing_tag:
        #Event has already taken place
        return None

    racing_href = racing_tag['href']
    race_time = racing_tag['data-time']
    race_title = racing_tag['title']
    return Event(racing_href, race_time, race_title)


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

# if __name__ == '__main__':
#     main()

