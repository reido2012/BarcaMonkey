import requests
# import xmltodict
import datetime
import os
# import gzip
import pytz
from .SmarketsEvent import SmarketsEvent
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


class Session:
    def __init__(self):
        self.session_token = self.get_session_token()
        self.events_for_the_day = None

    def get_session_token(self):
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

    def get_events(self):
        now = datetime.datetime.now(TZ)
        curr_day = now.strftime("%Y-%m-%dT00:00:00Z")
        request_data = self._create_event_request(curr_day)
        r = requests.get(f"{BASE}/v3/events/", params=request_data)
        all_events = r.json()
        all_events = all_events['events']

        print("Events")
        print("*" * 40)
        event = all_events[0]
        event_id = event['id']

        event_obj = {
            'id': event_id,
            'url':  "https://smarkets.com/event/" + event_id + event['full_slug'],
            'location': event['short_name'].split("@ ")[1].lower(),
            'type': event['type'],
            'inplay_enabled': event['inplay_enabled'],
            'time': event['name'],
            'description': event['description'],
            'title': event['short_name'],
            'datetime': datetime.datetime.strptime(event['start_datetime'], '%Y-%m-%dT%H:%M:%SZ').astimezone(TZ),
            'parent': event['parent_id'],
            'date': event['start_date'],
            'state': event['state']
        }

        smarkets_event = SmarketsEvent(event_obj)

        print(smarkets_event.id)
        pprint(event)
        self.get_event_market(smarkets_event)

    def get_event_market(self, smarkets_event):
        # event_id can be a list of event_ids, same with contracts
        r = requests.get(f"{BASE}/v3/events/{se.id}/markets/", params={'limit_by_event': 1})
        markets = r.json()['markets']
        market = markets[0]
        market_id = market['id']
        print("Market ID")
        print("*" * 40)
        pprint(market_id)
        self.get_market_contracts(market_id, smarkets_event)

    def get_market_contracts(self, market_id, smarkets_event):
        r = requests.get(f"{BASE}/v3/markets/{market_id}/contracts/", params={})
        contracts = r.json()['contracts']
        print("Contracts")
        print("*" * 40)
        pprint(contracts)

        quotes = self.get_contract_quotes(market_id, contracts)
        smarkets_event.create_horse_odds(contracts, quotes)

        pass

    def get_contract_last_executed_prices(self, market_id, contracts):
        r = requests.get(f"{BASE}/v3/markets/{market_id}/last_executed_prices/")
        prices = r.json()['last_executed_prices']

        print("Last Executed Prices")
        pprint(prices)

    def get_contract_quotes(self, market_id, contracts):
        r = requests.get(f"{BASE}/v3/markets/{market_id}/quotes/")
        quotes = r.json()

        self.process_contract_quotes(quotes)

        print("Quotes:")
        pprint(quotes)
        return quotes
    def process_contract_quotes(self, quotes):

        for contract_id, quote in quotes.items():
            quotes[contract_id] = self.format_quote(quote)

    def format_quote(self, quote):
        bids = quote['bids']
        offers = quote['offers']

        if bids:
            # Blue
            bid = self._convert_tick(bids[0])
        else:
            bid = None

        if offers:
            # Green
            offer = self._convert_tick(offers[0])
        else:
            offer = None

        quote['bids'] = bid
        quote['offers'] = offer

        return quote

    def _convert_tick(self, tick):
        """
        Converts the quantity and price of a tick to the format that matches the website.

        Quantity is the sum of the total pot (back+lay) in case the order is matched
        The units are 1/100 of a UK penny.

        This price is in percentage basis points.
        Example: 5000 = 50%
        To convert it to decimal odds, just divide 10000 by it
        Example: 10000 / 5000 = 2.0 (decimal odds).

        :param tick:
        :return: tick
        """
        converted_price = 10000/tick['price']
        available = (tick['price'] * tick['quantity'])/int(1e8)

        tick['quantity'] = round(available, 2)
        tick['price'] = round(converted_price, 2)

        return tick

    def _create_event_request(self, curr_day):
        # Full list of filters https://docs.smarkets.com/#/events/get_events
        data = dict(
            state=["upcoming"],
            type=["horse_racing_race"],
            type_domain=["horse_racing"],
            type_scope=["single_event"],
            start_date_min=curr_day,
            with_new_type=True,
            inplay_enabled=False,
            include_hidden=False,
            token=self.session_token
        )

        return data


def main():
    sess = Session()
    sess.get_events()


if __name__ == "__main__":
    main()
