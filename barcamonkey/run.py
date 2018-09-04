import datetime

from smarkets import Smarkets
from monkey import Monkey
from oddschecker import scraper


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
        scraper.run_scraper()
    except Exception as e:
        print("Exception in Scraper")
        print(e)
        return 0
    smarkets = Smarkets.SmarketsParser()
    smarkets.write_or_update_events()


def get_comparison_results():
    date_obj = datetime.datetime.now()
    if date_obj.hour < 21:
        date_str = str(date_obj.year) + "-" + '{:02d}'.format(date_obj.month) + "-" + '{:02d}'.format(date_obj.day)
    else:
        date_str = str(date_obj.year) + "-" + '{:02d}'.format(date_obj.month) + "-" + '{:02d}'.format(date_obj.day + 1)
    print(f"Date Str: {date_str}")

    monkey_comparer = Monkey.Monkey()
    return monkey_comparer.compare_events(date_str)


def main():
    # date_obj = datetime.datetime.now()
    # date_str = str(date_obj.year) + "-" + '{:02d}'.format(date_obj.month) + "-" + '{:02d}'.format(date_obj.day)
    # print(f"Date Str: {date_str}")

    scraper.run_scraper()
    # smarkets = Smarkets.SmarketsParser()
    # smarkets.write_or_update_events()

    # monkey_comparer = Monkey.Monkey()
    # all_results = monkey_comparer.compare_events(date_str)
    # print(all_results)
    # messages = create_messages_from_results(all_results)
    # print(messages)



def calculate_profit(smarkets_odd, odds_checker):
    return 0.98 * ((10 * odds_checker)/smarkets_odd-0.02) - 10


if __name__ == '__main__':
    main()
