import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from oddschecker.bookie_codes import BOOKIE_NAME_TO_INDEX

BARCAMONKEY_BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class OddsCheckerAutoBettor:

    def __init__(self, email_address, phantom=False,
                 user_data_path="/Users/omarreid/Library/Application\ Support/Google/Chrome/Default"):
        self.email_address = email_address

        opts = Options()
        opts.add_argument("user-data-dir=" + user_data_path)

        if phantom:
            self.driver = webdriver.PhantomJS()
            self.driver.set_window_size(1120, 550)
        else:
            self.driver = webdriver.Chrome(BARCAMONKEY_BASE_PATH + "/assets/chromedriver", chrome_options=opts)

    def place_bet(self, event_url, bookie, horse_name, expected_odds):

        self.driver.get(event_url)

        horse_row = self.driver.find_element_by_xpath(f"//tr[@data-bname='{horse_name}']")
        odds_list = horse_row.find_elements_by_tag_name("td")
        index = BOOKIE_NAME_TO_INDEX[bookie] + 3
        odds_button = odds_list[index]
        print(odds_button)
        print(f"Odds On Page: {odds_button.get_attribute('data-odig')}")
        print(f"Expected Odds: {expected_odds}")
        horse_odd = odds_button.get_attribute('data-odig')

        if horse_odd == "SP":
            return

        if "/" in horse_odd:
            horse_odd = self._get_decimal_odd(horse_odd)

        horse_odd = float(horse_odd)
        print(f"Horse Odds: {horse_odd}")
        print(f"Expected Odds: {float(expected_odds)}")
        if horse_odd == float(expected_odds):
            print("Odds Are As Expected -- Openning Betting Dialog")
            self._click_via_script(odds_button)

            # Login to bookie

            if self.driver.find_element_by_xpath(f"//span[@ng-click='BookieAreaController.showLogin()']"):
                # Login Via Modal
                login_button = self.driver.find_element_by_xpath(f"//span[@ng-click='BookieAreaController.showLogin()']")

                username_input = self.driver.find_element_by_xpath(f"//input[@id='username']")
                password_input = self.driver.find_element_by_xpath(f"//input[@id='password']")
            else:
                # Login Via Betslip
                login_button = None
                pass

            # If login button doesn't exist it means we have a bet slip open already
            print(login_button)
            self._click_via_script(login_button)

            time.sleep(1)
            while True:
                pass
        else:
            print("Odds Are Not What Expected")

    def _click_via_script(self, clickable_elem):
        self.driver.execute_script("arguments[0].click();", clickable_elem)

    def _get_decimal_odd(self, horse_odd):
        numerator, denominator = horse_odd.split("/")
        numerator = float(numerator)
        denominator = float(denominator)
        return (numerator / denominator) + 1.00
