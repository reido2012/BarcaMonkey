import datetime
import traceback
import pytz
from smarkets import Smarkets

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


    smarkets = Smarkets.SmarketsParser()
    smarkets.write_or_update_events()
    s8_scraper.run_scraper()
    scraper.run_scraper()

    monkey_comparer = Monkey.Monkey()
    all_results = monkey_comparer.compare_events(date_str)
    print(all_results)


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
        smarkets = Smarkets.SmarketsParser()
        smarkets.write_or_update_events()
    except Exception as e:
        print("Exception in Smarkets")
        traceback.print_exc()
        raise Exception

    try:
        scraper.run_scraper()
    except Exception as e:
        print("Exception in OddsChecker Scraper")
        print(e)
        raise Exception

    try:
        s8_scraper.run_scraper()
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



# def calculate_profit(smarkets_odd, odds_checker):
#     return 0.98 * ((10 * odds_checker)/smarkets_odd-0.02) - 10


if __name__ == '__main__':
    debug()
