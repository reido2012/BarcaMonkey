import datetime
import traceback
import pytz
import os
from smarkets import Smarkets

from monkey import Monkey
from oddschecker import scraper
from twilio.rest import Client

TZ = pytz.timezone('Europe/London')


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

    try:
        scraper.run_scraper()
    except Exception as e:
        print("Exception in Scraper")
        print(e)
        return 0


def get_comparison_results(current_day_limit=21):
    date_obj = datetime.datetime.now(TZ)
    if date_obj.hour < current_day_limit:
        date_str = str(date_obj.year) + "-" + '{:02d}'.format(date_obj.month) + "-" + '{:02d}'.format(date_obj.day)
    else:
        date_str = str(date_obj.year) + "-" + '{:02d}'.format(date_obj.month) + "-" + '{:02d}'.format(date_obj.day + 1)
    print(f"Date Str: {date_str}")

    monkey_comparer = Monkey.Monkey()
    return monkey_comparer.compare_events(date_str)


def make_call(phone_number):
    # Your Account Sid and Auth Token from twilio.com/console
    account_sid = os.environ.get('TWILIO_ACC_SID')
    auth_token = os.environ.get('TWILIO_AUTH')

    client = Client(account_sid, auth_token)

    call = client.calls.create(
                            url='http://demo.twilio.com/docs/voice.xml',
                            to=phone_number,
                            from_='+447492885157'
                        )

    print(call.sid)


def main():
    # date_obj = datetime.datetime.now()
    # date_str = str(date_obj.year) + "-" + '{:02d}'.format(date_obj.month) + "-" + '{:02d}'.format(date_obj.day)
    # print(f"Date Str: {date_str}")

    # scraper.run_scraper()
    # smarkets = Smarkets.SmarketsParser()
    # smarkets.write_or_update_events()

    # monkey_comparer = Monkey.Monkey()
    # all_results = monkey_comparer.compare_events(date_str)
    # print(all_results)
    # messages = create_messages_from_results(all_results)
    # print(messages)
    # make_call('+447934345900')
    pass


def calculate_profit(smarkets_odd, odds_checker):
    return 0.98 * ((10 * odds_checker)/smarkets_odd-0.02) - 10


if __name__ == '__main__':
    main()
