import time
import os
import string
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options


BARCAMONKEY_BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIN_BET = 0.05

class SmarketsAutoBettor:
    """
    This class contains methods that create a selenium webdriver instance to place a bet on smarkets
    """
    # Should take info that it needs to make a bet on smarkets
    # + debug mode - runs in chrome otherwise use phantomjs
    def __init__(self, email_address, phantom=False, user_data_path="/Users/omarreid/Library/Application\ Support/Google/Chrome/Default"):
        self.email_address = email_address

        opts = Options()
        opts.add_argument("user-data-dir=" + user_data_path)

        if phantom:
            self.driver = webdriver.PhantomJS()
            self.driver.set_window_size(1120, 550)
        else:
            self.driver = webdriver.Chrome(BARCAMONKEY_BASE_PATH + "/assets/chromedriver", chrome_options=opts)

        # set timeout information
        # driver.set_page_load_timeout(15)


    def bet_on_smarkets(self, smarkets_url, horse_name, expected_horse_odds, expected_availability):
        self._sign_in_to_smarkets(smarkets_url)
        self._place_bet(smarkets_url, horse_name, expected_horse_odds, expected_availability)

        while True:
            pass
        pass


    def _place_bet(self, smarkets_url, horse_name, odds,available):
        """
        Given an event, a horse and its odds, attempt to place a bet on the horse
        :param smarkets_url: URL of the event on Smarkets
        :param odds: The odds of the horse
        :param horse_name: Name of the horse
        :return: True if successful or False
        """

        horse_names = self.driver.find_elements_by_class_name('name')

        target_horse_name_container = None
        horse_to_find_name = self._format_horse_name(horse_name)

        for horse_name_container in horse_names:
            container_formattted_horse_name = self._format_horse_name(horse_name_container.text)

            if container_formattted_horse_name == horse_to_find_name:
                print(horse_name_container)
                print(container_formattted_horse_name)
                target_horse_name_container = horse_name_container
                break

        if not target_horse_name_container:
            print("HORSE NOT FOUND")
            # TODO: Throw a horse not found error

        print(f"Target Horse Found: {target_horse_name_container.text}")

        horse_row = target_horse_name_container


        # TODO: Put this in separate method
        # TODO: If there's no picture it should be range(4)
        for _ in range(5):
            horse_row = horse_row.find_element_by_xpath("..")

        if horse_row.find_element_by_xpath(".//span[@class='price tick sell  ']"):
            price_button_container = horse_row.find_element_by_xpath(".//span[@class='price tick sell  ']")
        else:
            price_button_container = horse_row.find_element_by_xpath(".//span[@class='price tick sell empty']")

        odds_on_page = price_button_container.find_element_by_xpath(".//span[@class='formatted-price numeric-value']")

        print("Odds On Page")
        print(odds_on_page)

        print("Price Button Container - Text")
        print(price_button_container.text)

        price_button_container.click()

        # To make  balance and liability equal : bal/(stake -1 )
        if not float(price_button_container.text) == float(odds):
            # TODO: Throw a incorrect odds error
            print("Odds Are NOT As Expected Throw Error")

        # Input the bet you want to make
        # contains(@class, 'class1') and contains(@class, 'class2')
        # @class='param-text-input text-input numeric-value'
        bet_popup = self.driver.find_element_by_xpath("//div[@class='bet-widget -desktop']")
        back_stake_container = bet_popup.find_element_by_xpath(".//input[contains(@class, 'param-text-input') and "
                                                               "contains(@class, 'text-input') and contains(@class, "
                                                               "'numeric-value')]")
        # This is a placeholder
        back_stake_container.send_keys(str(MIN_BET))

        # Check liability and make sure it is less than your balance
        liability_value = bet_popup.find_element_by_xpath(".//span[@class='bet-payout-item']").text
        liability_value = float(liability_value.replace("£", "").replace("RETURN", ""))
        print(f"Liability Value: {liability_value}")

        account_balance = self.driver.find_element_by_xpath("//div[@class='finance-detail']").text
        account_balance = float(account_balance.replace("BALANCE\n£", ""))
        print(f"Account Balance: {account_balance}")



    def _sign_in_to_smarkets(self, smarkets_url):
        time.sleep(0.5)
        self.driver.get(smarkets_url)

        while self.driver.current_url != smarkets_url:
            time.sleep(1)
            self.driver.get(smarkets_url)
            time.sleep(1)

        time.sleep(1)

        # Check if Smarkets kept us logged in
        try:
            self.driver.find_element_by_xpath("//a[@id='header-login']")
            already_logged_in = False
        except NoSuchElementException as e:
            already_logged_in = True

        if not already_logged_in:
            login_button = self.driver.find_element_by_xpath("//a[@id='header-login']")
            while login_button is None:
                login_button = self.driver.find_element_by_xpath("//a[@id='header-login']")

            time.sleep(1)
            login_button.click()

            email_input = self.driver.find_element_by_xpath("//input[@id='login-form-email']")
            while email_input is None:
                email_input = self.driver.find_element_by_xpath("//input[@id='login-form-email']")

            email_input.send_keys(self.email_address)

            smarkets_pass = os.environ.get('SMARKETS_PASS')
            password_input = self.driver.find_element_by_xpath("//input[@id='login-form-password']")
            password_input.send_keys(smarkets_pass)

            submit_login_button = self.driver.find_element_by_xpath("//button[@type='submit' and contains(text(), 'Log In')]")
            time.sleep(0.5)
            submit_login_button.click()
            time.sleep(2)

    def _format_horse_name(self, horse_name):
        translator = str.maketrans('', '', string.punctuation)
        horse_name = horse_name.lower().replace(" ", "")
        horse_name.translate(translator)
        return horse_name
