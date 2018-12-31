import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

BARCAMONKEY_BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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
        print()


        if phantom:
            self.driver = webdriver.PhantomJS()
            self.driver.set_window_size(1120, 550)
        else:
            self.driver = webdriver.Chrome(BARCAMONKEY_BASE_PATH + "/assets/chromedriver", chrome_options=opts)

    def place_bet(self, smarkets_url, odds, horse_name, available):
        """
        Given an event, a horse and its odds, attempt to place a bet on the horse
        :param smarkets_url: URL of the event on Smarkets
        :param odds: The odds of the horse
        :param horse_name: Name of the horse
        :return: True if successful or False
        """
        pass

    def sign_in_to_smarkets(self, smarkets_url):
        self.driver.get(smarkets_url)

        login_button = self.driver.find_element_by_xpath("//a[@id='header-login']")
        while login_button is None:
            login_button = self.driver.find_element_by_xpath("//a[@id='header-login']")

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

        while True:
            pass

