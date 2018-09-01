import datetime

from smarkets import Smarkets
from monkey import Monkey
from oddschecker import scraper


def get_results():
    get_data()
    return get_comparison_results()


def get_data():
    scraper.run_scraper()
    smarkets = Smarkets.SmarketsParser()
    smarkets.write_or_update_events()


def get_comparison_results():
    date_obj = datetime.datetime.now()
    date_str = str(date_obj.year) + "-" + '{:02d}'.format(date_obj.month) + "-" + '{:02d}'.format(date_obj.day)
    print(f"Date Str: {date_str}")

    monkey_comparer = Monkey.Monkey()
    return monkey_comparer.compare_events(date_str)


def main():
    date_obj = datetime.datetime.now()
    date_str = str(date_obj.year) + "-" + '{:02d}'.format(date_obj.month) + "-" + '{:02d}'.format(date_obj.day)
    print(f"Date Str: {date_str}")

    # scraper.run_scraper()
    # smarkets = Smarkets.SmarketsParser()
    # smarkets.write_or_update_events()

    monkey_comparer = Monkey.Monkey()
    all_results = monkey_comparer.compare_events(date_str)
    print(all_results)
    # messages = create_messages_from_results(all_results)
    # print(messages)


def create_messages_from_results(results):
    messages = []

    for (smarkets_url, oddschecker_url, event_results) in results:

        message = f"Smarkets URL: {smarkets_url} \n Odds Checker URL: {oddschecker_url} \n "

        for horse, difference_obj in event_results.items():
            horse_message = f"Horse: {horse} \n "
            message += horse_message
            for bookie_name, bookie_odds_obj in difference_obj.items():
                message += f"{bookie_name}: \n diff: {bookie_odds_obj['diff']} \n smarkets: {bookie_odds_obj['smarkets']} \n oddschecker: {bookie_odds_obj['odds_checker']}\n\n"

        messages.append(message)

    return messages


if __name__ == '__main__':
    main()
