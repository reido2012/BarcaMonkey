import os
import datetime
import requests
import pytz
from time import sleep
from .Sport888Event import Sport888Event

MAX_WORKERS = 4
CURRENT_DAY_LIMIT = 21
TZ = pytz.timezone('Europe/London')
BASE_RACE_URL = "https://www.888sport.com/horse-racing-betting/#/racing/event/"
MEETING_QUERY = "https://api.aws.kambicdn.com/offering/v2018/888/meeting/horse_racing.json?lang=en_GB&market=GB&client_id=2&channel_id=1&ncid=1537809853874"
EVENT_QUERY = "https://api.aws.kambicdn.com/offering/api/v2/888/betoffer/event/"
DIRNAME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run_scraper():

    result = requests.get(
        'https://api.aws.kambicdn.com/offering/v2018/888/meeting/horse_racing.json?lang=en_GB&market=GB&client_id=2&channel_id=1&ncid=1537809853874')

    meeting_ids = result.json()

    for meeting in meeting_ids:
        context = meeting['context']
        sport_name = context['sport']['englishName']
        course_name = context['course']['englishName']
        region_name = context['region']['englishName']

        if region_name != "UK & Ireland":
            continue

        if sport_name != "Horse Racing":
            continue

        events = meeting['events']

        for event in events:
            event_id = event['id']

            date_time = datetime.datetime.now(TZ)
            if date_time.hour < CURRENT_DAY_LIMIT:
                current_date = str(date_time.year) + "-" + '{:02d}'.format(
                    date_time.month) + "-" + '{:02d}'.format(date_time.day)
            else:
                current_date = str(date_time.year) + "-" + '{:02d}'.format(
                    date_time.month) + "-" + '{:02d}'.format(date_time.day + 1)

            event_obj = Sport888Event(event, current_date, course_name)

            race_obj = requests.get(
                f"{EVENT_QUERY}{event_id}.json?lang=en_GB&market=GB&client_id=2&channel_id=1&ncid=1537813014925")

            if race_obj.status_code == 429:
                sleep(1)
                race_obj = requests.get(
                    f"{EVENT_QUERY}{event_id}.json?lang=en_GB&market=GB&client_id=2&channel_id=1&ncid=1537813014925")

            race_obj = race_obj.json()

            if 'betoffers' not in race_obj:
                continue

            bet_offers = race_obj['betoffers'][0]  # 0 to Win
            outcomes = bet_offers['outcomes']

            event_obj.set_horses(outcomes)
            event_obj.send_to_json()

    print("Finished 888Sport Request")
