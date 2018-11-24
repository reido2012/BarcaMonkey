import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from oddschecker.bookie_codes import BOOKIE_NAME_TO_INDEX

def main(event_url, bookie, horse_name, expected_odds):
    opts = Options()
    opts.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, "
                      "like Gecko) Chrome/66.0.3359.139 Safari/537.36")
    driver = webdriver.Chrome('./assets/chromedriver', chrome_options=opts)

    driver.get(event_url)

    horse_row = driver.find_element_by_xpath(f"//tr[@data-bname='{horse_name}']")
    odds_list = horse_row.find_elements_by_tag_name("td")
    index = BOOKIE_NAME_TO_INDEX[bookie] + 1
    odds_button = odds_list[index]
    print(odds_button)
    print(f"Odds On Page: {odds_button.get_attribute('data-odig')}")
    print(f"Expected Odds: {expected_odds}")
    horse_odd = odds_button.get_attribute('data-odig')

    if horse_odd == "SP":
        return

    if "/" in horse_odd:
        horse_odd = get_decimal_odd(horse_odd)

    horse_odd = float(horse_odd)
    print(f"Horse Odds: {horse_odd}")
    print(f"Expected Odds: {float(expected_odds)}")
    if horse_odd == float(expected_odds):
        print("Odds Are As Expected -- Openning Betting Dialog")
        click_via_script(driver, odds_button)

        # Login to bookie

        if driver.find_element_by_xpath(f"//span[@ng-click='BookieAreaController.showLogin()']"):
            #Login Via Modal
            login_button = driver.find_element_by_xpath(f"//span[@ng-click='BookieAreaController.showLogin()']")

            username_input = driver.find_element_by_xpath(f"//input[@id='username']")
            password_input = driver.find_element_by_xpath(f"//input[@id='password']")
        else:
            #Login Via Betslip
            login_button = None
            pass

        #If login button doesn't exist it means we have a bet slip open already
        print(login_button)
        click_via_script(driver, login_button)

        time.sleep(1)
        while True:
            pass
    else:
        print("Odds Are Not What Expected")


# def login_padd

def click_via_script(driver, clickable_elem):
    driver.execute_script("arguments[0].click();", clickable_elem)


def get_decimal_odd(horse_odd):
    numerator, denominator = horse_odd.split("/")
    numerator = float(numerator)
    denominator = float(denominator)
    return (numerator / denominator) + 1.00


if __name__ == '__main__':
    main("https://www.oddschecker.com/horse-racing/gulfstream/23:36/winner", 'Paddy Power', 'Dreamingofmermaids', 9)
