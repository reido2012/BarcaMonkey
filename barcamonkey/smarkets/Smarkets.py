import requests
# import xmltodict
# import datetime
import os
# import gzip
import pytz
# from .SmarketsEvent import SmarketsEvent
from pprint import pprint
#
# from collections import OrderedDict
DIRNAME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TZ = pytz.timezone('Europe/London')
BASE = "https://api.smarkets.com"

# class SmarketsParser:
#     """
#     Handles downloading and parsing of the Smarkets XML odds feed
#
#     The XML feed is updated every few seconds but the information is delayed by 30 seconds.
#     """
#
#     #Date Format
#     #YEAR - MONTH - DAY
#
#     def __init__(self, current_day_limit=21):
#         self._XML_URL = "http://odds.smarkets.com/oddsfeed.xml.gz"
#
#         with requests.get(self._XML_URL) as r:
#             # r.encoding = 'utf-8'
#             # print(r.content.decode('utf-8'))
#             if r.encoding == 'UTF-8':
#                 self.xml_dict = xmltodict.parse(r.text)['odds']
#             else:
#                 filename = self._XML_URL.split("/")[-1]
#                 with open(filename, "wb") as f:
#                     r = requests.get(self._XML_URL)
#                     f.write(r.content)
#
#                 self.xml_dict = xmltodict.parse(gzip.GzipFile(filename))['odds']
#
#             self.date_time = datetime.datetime.now(TZ)
#             if self.date_time.hour < current_day_limit:
#                 self.current_date = str(self.date_time.year) + "-" + '{:02d}'.format(
#                     self.date_time.month) + "-" + '{:02d}'.format(self.date_time.day)
#             else:
#                 self.current_date = str(self.date_time.year) + "-" + '{:02d}'.format(
#                     self.date_time.month) + "-" + '{:02d}'.format(self.date_time.day + 1)
#
#     def write_or_update_events(self):
#         for event_obj in self.xml_dict['event']:
#             if event_obj['@type'] == 'Horse racing race' and event_obj['@date'] == self.current_date:
#
#                 if not event_obj['market']:
#                     continue
#
#                 new_event = SmarketsEvent(event_obj, self.current_date)
#
#                 if type(event_obj['market']) == OrderedDict:
#                     horses = event_obj['market']['contract']
#                 else:
#                     horses = event_obj['market'][0]['contract']
#
#                 sorted_horses = sorted(horses, key=lambda x: x['@slug'])
#                 new_event.set_horses(sorted_horses)
#                 new_event.send_to_json()
#
#         print("Finished Handling Smarkets")


def main():
    session_token = get_session_token()
    get_events()

def get_session_token():
    """
    Will return token that can be used to authenticate future requests
    The token is valid for 30 mins, but if we make an authenticated request with it it will be renewed for 30 more mins
    :return:
        session_token: Session token we use to
    """

    credentials = {
        "password": os.environ.get('SMARKETS_PASS'),
        "remember": True,
        "username": "oreid52@googlemail.com"
    }

    r = requests.post(BASE + '/v3/sessions/', json=credentials)
    result = r.json()
    session_token = result['token']
    return session_token

def get_events():
    pass


if __name__ == "__main__":
    main()
