import re
import time
import urllib.request
import os

from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium import webdriver

from selenium.webdriver.common.keys import Keys

from tinder.database.models import TinderUser, Image
from tinder.database import Session

from tinder.utils import files
from selenium.common.exceptions import NoSuchElementException


def firefox(location=None):
    firefox_profile = FirefoxProfile()
    firefox_profile.set_preference("geo.enabled", True)
    firefox_profile.set_preference("geo.provider.use_corelocation", True)

    firefox_profile.set_preference("geo.prompt.testing", True)
    firefox_profile.set_preference("geo.prompt.testing.allow", True)

    if location:
        firefox_profile.set_preference("geo.wifi.uri",
                                       'data:application/json,{"location": {"lat": %s, "lng": %s}, "accuracy": 100.0}' % (location.latitude, location.longitude))

    return webdriver.Firefox(firefox_profile=firefox_profile)


def chromium(location=None):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--disable-notifications')

    return webdriver.Chrome(chrome_options=chrome_options)


BROWSER_PROFILES = {
    'firefox': firefox,
    'chromium': chromium
}


def get_browser(browser, location=None, *args, **kwargs):
    if browser in BROWSER_PROFILES:
        return BROWSER_PROFILES[browser](*args, location=location, **kwargs)
    else:
        raise ValueError('Browser {} not defined!'.format(browser))


def download_images(images):
    for image in images:
        download_image(image.url, image.file_path)


def download_image(url, file_name):
    urllib.request.urlretrieve(url=url, filename=file_name)


class WebBot:
    def __init__(self, email, password, location=None, browser='firefox'):
        self.email = email
        self.password = password
        self.browser = get_browser(browser, location=location)

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
        name, age = '', None

        try:

            name_age = self.browser.find_element_by_xpath("//*[contains(@class, 'profileCard__nameAge')]").text

            if name_age:
                split_name_age = name_age.split()

                if split_name_age and len(split_name_age) == 2:
                    name, age = split_name_age

                    name = name.replace(',', '').strip()
                    age = int(age.replace(',', '').strip())
        except NoSuchElementException as e:
            print(e)
            print('Could not find name age element!')

        return name, age

    def get_image_url(self):
        return self.browser.find_element_by_xpath(
            "//*[contains(@class, 'profileCard__slider__img StretchedBox')]").get_attribute('src')

    def get_all_image_urls(self):
        """
        Find the top level stack element and then send the space key to iterate though user photos
        and at each iteration look for the newly loaded image if the image url already exists in the
        list then filter it out

        :return: image urls list if image urls are found if a element was not found exception
        """
        time.sleep(1)

        try:
            picture_elements = self.browser.find_element_by_xpath("//*[contains(@class, 'profileCard__slider')]")
        except NoSuchElementException as e:
            print(e)
            print('profileCard__slider element was not found')

            return []

        user_image_urls = []

        # If there is a no such element exception at an iteration of the for loop catch and return what
        # we have so far..
        try:

            for _ in range(6):
                # Sleep for 1 second or image url will not load
                time.sleep(1)

                # find a better way but this works for now...
                picture_elements.send_keys(Keys.SPACE)
                image_elements = picture_elements.find_elements_by_tag_name('img')
                temp_user_image_urls = list(map(lambda element: element.get_attribute('src'), image_elements))
                temp_user_image_urls = filter(lambda url: url not in user_image_urls, temp_user_image_urls)

                user_image_urls.extend(temp_user_image_urls)
        except NoSuchElementException as e:
            print(e)
            print('An image url could not be found!')

        return user_image_urls

    def get_next_image_button(self):
        return self.browser.find_elements_by_xpath("//*[contains(@class, 'pageButton')]")


def create_images(image_urls, images_file_path, tinder_user_name):
    images = []

    for i, image_url in enumerate(image_urls):
        image_number = i + 1
        file_path = get_tinder_user_image_filepath(images_file_path, tinder_user_name, image_number)
        image = Image(url=image_url, file_path=file_path, image_number=image_number)
        images.append(image)

    return images


def get_tinder_user_image_filepath(images_file_path, tinder_user_name, number):
    return '{}/{}/{}_{}.jpg'.format(images_file_path, tinder_user_name, tinder_user_name, number)


def get_tinder_user_image_dir(images_file_path, tinder_user_name):
    return '{}/{}'.format(images_file_path, tinder_user_name)


class AutoSwiper(WebBot):
    def __init__(self, *args, **kwargs):
        super(AutoSwiper, self).__init__(*args, **kwargs)
        self.images_file_path = '/Users/ericrincon/tinder_data/images'

        files.make_check_dir(self.images_file_path)

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
            image_urls = self.get_all_image_urls()

            session = Session()
            image_name = name

            check = files.make_check_dir(get_tinder_user_image_dir(self.images_file_path, image_name))

            while check:
                if '_' in name:
                    image_name, number = name.split()
                    number = int(number) + 1
                else:
                    number = 0
                image_name = '{}_{}'.format(image_name, number)

                check = files.make_check_dir(get_tinder_user_image_dir(self.images_file_path, image_name))

            images = create_images(image_urls, self.images_file_path, image_name)

            user = TinderUser(name=name, age=age, bio=bio_text,
                              images=images)
            download_images(images)

            session.add(user)
            session.commit()
            session.close()

            if not bio_checker.check(bio_text):
                print('Shes not into hookups!')
                self.swipe_left()
            else:
                self.swipe_right()

    def save_images(self, image_urls):
        for image_url in image_urls:
            file_name = ''
            download_image(image_url, file_name)


class BioCheck:
    def __init__(self):
        self.regex = [re.compile(r'not into hook ups|no hookups')]

    def check(self, bio):
        bio = bio.lower()
        for exp in self.regex:
            if exp.match(bio):
                return False
        return True
