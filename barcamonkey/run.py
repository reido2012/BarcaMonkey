import datetime

from smarkets import Smarkets
from monkey import Monkey
from oddschecker import scraper

def main():
    date_obj = datetime.datetime.now()
    date_str = str(date_obj.year) + "-" + '{:02d}'.format(date_obj.month) + "-" + '{:02d}'.format(date_obj.day)
    print(f"Date Str: {date_str}")

    scraper.run_scraper()
    smarkets = Smarkets.SmarketsParser()
    smarkets.write_or_update_events()

    monkey_comparer = Monkey.Monkey()
    monkey_comparer.compare_events(date_str)


if __name__ == '__main__':
    main()
