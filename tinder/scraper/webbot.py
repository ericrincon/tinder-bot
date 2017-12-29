import re
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as e
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import NoSuchElementException

import os
import urllib
import urllib2


from selenium.webdriver.common.keys import Keys


def firefox():
    firefox_profile = FirefoxProfile()
    firefox_profile.set_preference("geo.enabled", True)
    firefox_profile.set_preference("geo.provider.use_corelocation", True)

    firefox_profile.set_preference("geo.prompt.testing", True)
    firefox_profile.set_preference("geo.prompt.testing.allow", True)

    return webdriver.Firefox(firefox_profile=firefox_profile)



def chromium():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--disable-notifications')

    return webdriver.Chrome(chrome_options=chrome_options)


BROWSER_PROFILES = {
    'firefox': firefox,
    'chromium': chromium
}

def get_browser(browser):
    if browser in BROWSER_PROFILES:
        return BROWSER_PROFILES[browser]()
    else:
        raise ValueError('Browser {} not defined!'.format(browser))

class WebBot:
    def __init__(self, email, password, browser='firefox'):
        self.email = email
        self.password = password
        self.browser = get_browser(browser)

        self.browser.get('https://tinder.com/app/login')

    def get_bio(self):
        try:
            elem = self.browser.find_element_by_css_selector('body')
            elem.send_keys(Keys.ARROW_UP)
            profile_card = self.browser.find_element_by_xpath(
                '//div[@class="Py(10px) Px(16px) profileCard__bio Ta(start) Us(t) C($c-secondary) BreakWord Whs(pl)"]')
            profile_text = profile_card.find_element_by_class_name('text')

            return profile_text.text
        except Exception as e:
            print(e)

            return None

    def swipe_left(self):
        elem = self.browser.find_element_by_css_selector('body')
        elem.send_keys(Keys.ARROW_LEFT)

    def swipe_right(self):
        elem = self.browser.find_element_by_css_selector('body')
        elem.send_keys(Keys.ARROW_RIGHT)

    def login_facebook(self):
        time.sleep(5)

        try:
            login_button = self.browser.find_element_by_xpath('//button[@aria-label="Log in with Facebook"]')
            login_button.click()
            time.sleep(2)
            self.browser.switch_to_window(self.browser.window_handles[-1])

        except Exception as e:
            print(e)

        email_element = self.browser.find_element_by_name('email')
        password_element = self.browser.find_element_by_name('pass')

        email_element.send_keys(self.email)
        password_element.send_keys(self.password)

        login_button = self.browser.find_element_by_name('login')
        login_button.click()

        self.browser.switch_to_window(self.browser.window_handles[0])

    def get_name(self):
        name = self.browser.find_element_by_xpath(
            '//div[@class="profileCard__nameAge Lts($ls-s) C($c-base) Us(t) Fw($medium) Fz($ml)"]').text

        return name

    def start(self):
        pass

    def get_name_age(self):
        """
        Finds the element for the name and age in the profile and returns the name as a string and the age
        as an int
        :return:
        """
        name_age = self.browser.find_element_by_xpath("//*[contains(@class, 'profileCard__nameAge')]").text

        if name_age is None:
            return None, None
        name, age = name_age.split()

        name = name.strip()
        age = int(age.strip())

        return name, age

    def get_image_url(self):
        return self.browser.find_element_by_xpath("//*[contains(@class, 'profileCard__slider__img StretchedBox')]").get_attribute('src')

    def get_all_image_urls(self):
        time.sleep(1)
        picture_elements =  self.browser.find_element_by_xpath("//*[contains(@class, 'profileCard__slider')]")

        # picture_elements = self.browser.find_element_by_class_name('react-swipeable-view-container')
        user_image_urls = []

        for _ in range(6):
            time.sleep(1)
            # find a better way but this works for now...
            picture_elements.send_keys(Keys.SPACE)
            image_elements = picture_elements.find_elements_by_tag_name('img')
            temp_user_image_urls = list(map(lambda element: element.get_attribute('src'), image_elements))
            temp_user_image_urls = filter(lambda url: url not in user_image_urls, temp_user_image_urls)

            user_image_urls.extend(temp_user_image_urls)

        print(len(user_image_urls))

    def get_next_image_button(self):
        return self.browser.find_elements_by_xpath("//*[contains(@class, 'pageButton')]")

class AutoSwiper(WebBot):
    def start(self):

        self.login_facebook()

        time.sleep(5)

        next_button = self.browser.find_element_by_xpath(
            '//button[@class="button Lts($ls-s) Z(0) Whs(nw) Cur(p) Tt(u) Bdrs(100px) Px(24px) Py(0) H(40px) Mih(40px) Lh(40px) button--primary-shadow Pos(r) Ov(h) C(#fff) Bg($c-pink):h::b Trsdu($fast) Trsp($background) Bg($primary-gradient) StyledButton Fw($semibold)"]')
        next_button.click()

        next_button = self.browser.find_element_by_xpath(
            '//button[@class="button Lts($ls-s) Z(0) Whs(nw) Cur(p) Tt(u) Bdrs(100px) Px(24px) Py(0) H(40px) Mih(40px) Lh(40px) button--primary-shadow Pos(r) Ov(h) C(#fff) Bg($c-pink):h::b Trsdu($fast) Trsp($background) Bg($primary-gradient) StyledButton Fw($semibold)"]')
        next_button.click()

        great_button = self.browser.find_element_by_xpath(
            '//button[@class="button Lts($ls-s) Z(0) Whs(nw) Cur(p) Tt(u) Bdrs(100px) Px(24px) Py(0) H(40px) Mih(40px) Lh(40px) button--primary-shadow Pos(r) Ov(h) C(#fff) Bg($c-pink):h::b Trsdu($fast) Trsp($background) Bg($primary-gradient) StyledButton Fw($semibold)"]')
        great_button.click()
        time.sleep(10)
        not_interested_button = self.browser.find_element_by_xpath('//button[@aria-label="Not interested"]')
        not_interested_button.click()

        bio_checker = BioCheck()



        while True:
            time.sleep(2)
            bio_text = self.get_bio()

            if bio_text is None:
                bio_text = 'No bio!'
            name, age = self.get_name_age()

            self.get_all_image_urls()
            print(bio_text + '\n')

            if not bio_checker.check(bio_text):
                print('Shes not into hookups!')
                self.swipe_left()
            else:
                self.swipe_right()


class BioCheck:
    def __init__(self):
        self.regex = [re.compile(r'not into hook ups|no hookups')]

    def check(self, bio):
        bio = bio.lower()
        for exp in self.regex:
            if exp.match(bio):
                return False
        return True



