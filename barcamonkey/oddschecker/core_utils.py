import logging
import requests
import socket
import ssl
import sys
import time


from bs4 import BeautifulSoup
from scraper_exceptions import Exception404
from time import sleep


def get_soup(url):
    if 'oddschecker.com/' not in url:
        url = 'https://www.oddschecker.com' + url

    # nap_time_sec = 1
    # logging.debug('Script is going to sleep for {} (Amazon throttling). ZZZzzzZZZzz.'.format(nap_time_sec))
    #sleep(nap_time_sec)
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36'
    }
    logging.debug('-> to OddsChecker : {}'.format(url))

    return handle_url_request(url, header)


def handle_url_request(url, header):
    out = make_request(header, url)

    if out:
        if out.status_code == 404:
            logging.error("404 For Url: ", url)
            raise Exception404
        else:
            assert out.status_code == 200

        soup = run_bs4(out)
    else:
        print(f"Sleeping for 5 Seconds")
        time.sleep(5)
        try:
            out = make_request(header, url)
            if out.status_code == 404:
                logging.error("404 For Url: ", url)
                raise Exception404
            else:
                assert out.status_code == 200

                soup = run_bs4(out)
        except Exception as e:
            print(f"Exception When Handling URL: {e}")
            raise Exception
    return soup


def make_request(header, url):
    time.sleep(1)
    try:
        out = requests.get(url, headers=header)
    except ssl.SSLEOFError as ssle:
        logging.info("SSL Error - In Requests")
        print(ssle)
        logging.info("Sleeping for 10 Seconds - Will attempt again")
        time.sleep(20)
        out = requests.get(url, headers=header)
    except socket.gaierror as e:
        # if e.errno == socket.EAI_AGAIN:
        logging.info("In Requests - Temporary Failure In Name Resolution")
        logging.info("Sleeping for 10 Seconds")
        time.sleep(20)
        out = requests.get(url, headers=header)
    except requests.exceptions.ConnectionError as ce:
        logging.info('Connection Error CAUGHT in __MAIN__')
        logging.info(ce)
        logging.info("Sleeping for 20 Seconds")
        time.sleep(20)
        out = requests.get(url, headers=header)

    return out


def run_bs4(out):
    soup = BeautifulSoup(out.content, 'html.parser')
    ##if 'captcha' in str(soup):
    #   raise BannedException('Your bot has been detected. Please wait a while.')
    return soup
