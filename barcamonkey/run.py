import datetime
import traceback
import pytz
import time

from smarkets import Smarkets
from smarkets_autobettor import smarkets_autobettor
from monkey import Monkey
from oddschecker import scraper
from sport888 import scraper as s8_scraper


TZ = pytz.timezone('Europe/London')


def debug():
    date_obj = datetime.datetime.now(TZ)
    if date_obj.hour < 21:
        date_str = str(date_obj.year) + "-" + '{:02d}'.format(date_obj.month) + "-" + '{:02d}'.format(date_obj.day)
    else:
        date_str = str(date_obj.year) + "-" + '{:02d}'.format(date_obj.month) + "-" + '{:02d}'.format(date_obj.day + 1)
    print(f"Date Str: {date_str}")

    smarkets_s = time.time()
    smarkets = Smarkets.SmarketsParser()
    smarkets.write_or_update_events()
    smarkets_f = time.time()

    s8_s = time.time()
    s8_scraper.run_scraper_concurrent()
    s8_f = time.time()

    oddschecker_s = time.time()
    scraper.run_scraper()
    oddschecker_f = time.time()

    print(f"Oddschecker Time: {oddschecker_f - oddschecker_s}")
    print(f"Sport888 Time: {s8_f - s8_s}")
    print(f"Smarkets Time: {smarkets_f - smarkets_s}")

    monkey_comparer = Monkey.Monkey()
    all_results = monkey_comparer.compare_events(date_str)
    print(all_results)


def test_auto_betting():
    auto_bettor = smarkets_autobettor.SmarketsAutoBettor("oreid52@googlemail.com")
    # auto_bettor.sign_in_to_smarkets("https://smarkets.com/event/1338869/sport/horse-racing/huntingdon/2019/01/11/13:00")
    auto_bettor.bet_on_smarkets('https://smarkets.com/event/1366429/sport/horse-racing/newcastle/2019/01/17/19:25',
                                'Royal Mezyan', 9.8, 27)

def get_results():
    try:
        get_data()
    except Exception as e:
        print("Exception Occurred")
        print(e)
        return 0
    return get_comparison_results()


def get_data():
    try:
        #Can be put in a thread
        smarkets = Smarkets.SmarketsParser()
        smarkets.write_or_update_events()
    except Exception as e:
        print("Exception in Smarkets")
        traceback.print_exc()
        raise Exception

    try:
        #This uses multiple threads to scrape the individual event pages
        scraper.run_scraper()
    except Exception as e:
        print("Exception in OddsChecker Scraper")
        print(e)
        raise Exception

    try:
        s8_scraper.run_scraper_concurrent()
    except Exception as e:
        print("Exception in 888 Scraper")
        print(e)
        raise Exception


def get_comparison_results(current_day_limit=21):
    date_obj = datetime.datetime.now(TZ)
    if date_obj.hour < current_day_limit:
        date_str = str(date_obj.year) + "-" + '{:02d}'.format(date_obj.month) + "-" + '{:02d}'.format(date_obj.day)
    else:
        date_str = str(date_obj.year) + "-" + '{:02d}'.format(date_obj.month) + "-" + '{:02d}'.format(date_obj.day + 1)
    print(f"Date Str: {date_str}")

    monkey_comparer = Monkey.Monkey()
    return monkey_comparer.compare_events(date_str)


if __name__ == '__main__':
    # debug()
    test_auto_betting()