import re
import time
import sys
import robobrowser
import logging

from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium import webdriver

from selenium.webdriver.common.keys import Keys

from database.db.models.user import TinderUser, Image
from database.db import Session

from host.host.utils import files
from selenium.common.exceptions import NoSuchElementException, WebDriverException

from host.host.utils import images as utils_images

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
file_handler = logging.FileHandler('errors.log')
formatter = logging.Formatter(
    '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)
logger.addHandler(handler)
logger.addHandler(file_handler)
logger.setLevel(logging.ERROR)


def firefox(*args, **kwargs):
    firefox_profile = FirefoxProfile()
    firefox_profile.set_preference("geo.prompt.testing", True)
    firefox_profile.set_preference("geo.prompt.testing.allow", True)

    return webdriver.Firefox(firefox_profile=firefox_profile)


def chromium(*args, **kwargs):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--disable-notifications')

    return webdriver.Chrome(chrome_options=chrome_options)


BROWSER_PROFILES = {
    'firefox': firefox,
    'chromium': chromium
}


def get_browser(browser, *args, **kwargs):
    if browser in BROWSER_PROFILES:
        return BROWSER_PROFILES[browser](*args, **kwargs)
    else:
        raise ValueError('Browser {} not defined!'.format(browser))


class WebBot:
    def __init__(self, email, password, sleep_multiplier: int = 1, browser='firefox', debug=False):
        self.email = email
        self.password = password
        self.browser = get_browser(browser)
        self.debug = debug
        self.sleep_multiplier = sleep_multiplier

        self.browser.get('https://tinder.com/app/login')

    def get_bio(self):

        time.sleep(2)


        try:
            elem = self.browser.find_element_by_css_selector('body')
            elem.send_keys(Keys.ARROW_UP)
            time.sleep(2 * self.sleep_multiplier)

            profile_card = self.browser.find_element_by_xpath("//*[contains(@class, 'profileCard__bio')]")
            profile_text = profile_card.find_element_by_css_selector('span')

            return profile_text.text

        except Exception as e:
            logger.error("Bio not found: {}".format(e))

            return None

    def swipe_left(self):
        get_body_element = lambda: self.browser.find_element_by_css_selector('body')
        get_body_element().send_keys(Keys.ARROW_LEFT)

    def swipe_right(self):
        get_body_element = lambda: self.browser.find_element_by_css_selector('body')
        get_body_element().send_keys(Keys.ARROW_RIGHT)

    def login_facebook(self):
        time.sleep(5 * self.sleep_multiplier)

        try:
            login_button = self.browser.find_element_by_xpath('//button[@aria-label="Log in with Facebook"]')
            login_button.click()
            time.sleep(2 * self.sleep_multiplier)
            self.browser.switch_to_window(self.browser.window_handles[-1])

        except Exception as e:
            logger.error("Could not log into facebook: {}".format(e))

        get_email_element = lambda: self.browser.find_element_by_name('email')
        get_password_element = lambda: self.browser.find_element_by_name('pass')

        get_email_element().send_keys(self.email)
        get_password_element().send_keys(self.password)

        login_button = self.browser.find_element_by_name('login')
        login_button.click()

        self.browser.switch_to_window(self.browser.window_handles[0])

    def get_share_button(self):
        """
        Locates the allow sharing button option at the start of the host user
        login flow
        :return:
        """

        share_button = self.browser.find_element_by_xpath('//*[@aria-label="Great!"]')

        return share_button

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
        name, age = None, None

        try:

            profilecard_header_info = self.browser.find_element_by_xpath(
                "//*[contains(@class, 'Ov(h) Ws(nw) Ell')]")
            name_age = profilecard_header_info.find_element_by_xpath(
                "//*[contains(@class, 'My(2px) C($c-base) Us(t) D(f) Ai(b) Maw(90%)')]").text

            if name_age:
                split_name_age = name_age.split()

                if split_name_age and len(split_name_age) == 2:
                    name, age = split_name_age

                    name = name.replace(',', '').strip()
                    age = int(age.replace(',', '').strip())
        except NoSuchElementException as e:
            logger.error("Failed with exception: {} - Could not find name age element!".format(e))

            return None, None

        return name, age

    def get_profile_expand(self):

        return self.browser.find_element_by_xpath("//*[contains(@class, 'recCard__openProfile')]")

    def get_profile_card_element(self):
        return self.browser.find_element_by_xpath("//*[contains(@class, 'recsCardboard__cards')]")

    def get_image_slider_element(self):
        """
        Gets the element where the image is located

        Note: this changes.. Last time the imge was located in an attrivute
        :return:
        """
        return self.browser.find_element_by_xpath("//*[contains(@class, 'react-swipeable-view-container')")

    def get_image_url(self, element):
        """

        :param element:
        :return:
        """
        style = element.get("style")
        url = ""

        if style is not None and style != "":
            url = re.findall("(?<=url\(\")(.*)(?=\"\))", style)
            url = url[0] if len(url) > 0 else ""

        return url

    def get_all_image_urls(self):
        """
        Find the top level stack element and then send the space key to iterate though user photos
        and at each iteration look for the newly loaded image if the image url already exists in the
        list then filter it out

        :return: image urls list if image urls are found if a element was not found exception
        """
        time.sleep(1 * self.sleep_multiplier)

        try:

            # soup = BeautifulSoup(self.browser.page_source)
            # results = soup.find_all('div', attrs={"class": "home-summary-row"})
            get_picture_elements = lambda: self.browser.find_element_by_xpath(
                "//*[contains(@class, 'profileCard__slider')]")
        except NoSuchElementException as e:
            logger.error("Failed to get image urls: {}".format(e))

            return []

        user_image_urls = []

        # If there is a no such element exception at an iteration of the for loop catch and return what
        # we have so far..
        try:

            for _ in range(9):
                # Sleep for 1 second or image url will not load
                time.sleep(2)

                # find a better way but this works for now...
                get_picture_elements().send_keys(Keys.SPACE)
                soup = BeautifulSoup(self.browser.page_source)
                results = soup.find_all('div', attrs={"class": "profileCard__slider__img"})

                image_urls = list(map(lambda element: self.get_image_url(element), results))
                image_urls = list(filter(lambda url: url != "", image_urls))
                image_urls = list(filter(lambda url: url not in user_image_urls, image_urls))

                user_image_urls.extend(image_urls)

        except NoSuchElementException as e:
            logger.error("An image url could not be found!\n{}".format(e))

            return None

        return user_image_urls

    def get_next_image_button(self):
        return self.browser.find_elements_by_xpath("//*[contains(@class, 'pageButton')]")

    def get_next_button_element(self):
        return self.browser.find_element_by_xpath("//button[@aria-label='Next']")

    def get_enable_notifications_not_interested(self):
        return self.browser.find_element_by_xpath("//button[@aria-label='Not interested']")

    def get_matches_element(self):
        return self.browser.find_elements_by_xpath("//button[@aria-label='Not interested']")

    def get_location_allow_button(self):
        return self.browser.find_element_by_xpath("//button[@aria-label='Allow']")


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
        self.profile_count = 0

        files.make_check_dir(self.images_file_path)

    def restart_check(self):
        if self.debug:
            response = input("There was an error, press any button to continue")

        sys.stdout.write('Error: Elements are gone restarting...')
        sys.stdout.flush()

        input("Press Enter to restart...")

        self.browser.close()

    def start(self):
        self.login_facebook()

        time.sleep(10)

        location_button = self.get_location_allow_button()
        location_button.click()

        time.sleep(10)
        not_interested_button = self.get_enable_notifications_not_interested()
        not_interested_button.click()

        bio_checker = BioCheck()

        while True:
            console_info = ''

            time.sleep(2 * self.sleep_multiplier)

            bio_text = self.get_bio()

            if bio_text is None:
                bio_text = 'No bio!'
            name, age = self.get_name_age()
            image_urls = self.get_all_image_urls()

            session = Session()
            image_name = name

            check = files.make_check_dir(get_tinder_user_image_dir(self.images_file_path, image_name))

            bio_info = 'name: {} age: {} bio: {}\n'.format(name is not None, age is not None,
                                                           bio_text is not None)
            console_info += bio_info

            while check:
                if image_name and '_' in image_name:
                    image_name, number = image_name.split('_')
                    number = int(number) + 1
                else:
                    number = 0
                image_name = '{}_{}'.format(image_name, number)

                check = files.make_check_dir(get_tinder_user_image_dir(self.images_file_path, image_name))

            if image_urls is not None:
                images = create_images(image_urls, self.images_file_path, image_name)

                user = TinderUser(name=name, age=age, bio=bio_text,
                                  images=images)
                utils_images.download_images(images)

                session.add(user)
                session.commit()
                session.close()

                self.profile_count += 1
                profile_add_info = '\nAdded {} of age {} with {} images\n'.format(name, age, len(images))
                console_info += profile_add_info

                nb_scarped_text = '\n{} profiles scraped'.format(self.profile_count)

                console_info += nb_scarped_text

                sys.stdout.write(console_info)
                sys.stdout.flush()

            if not bio_checker.check(bio_text):
                self.swipe_left()
            else:
                self.swipe_right()

            try:
                time.sleep(7 * self.sleep_multiplier)
                continue_swiping_element = lambda: self.browser.find_element_by_xpath(
                    "//*[contains(text(), 'Keep Swiping')]")
                continue_swiping_element().click()



            except (NoSuchElementException, WebDriverException):  # If didnt match with person then go on
                pass


class BioCheck:
    def __init__(self):
        self.regex = [re.compile(r"not into hook ups|no hookups")]

    def check(self, bio):

        bio = bio.lower()

        for exp in self.regex:
            if exp.match(bio):
                return False

        return True


class TokenBot:
    """
    Automates the retrieval of an authtoken and a user id
    """

    def __init__(self, user_agent=None, auth_url=None):
        self.user_agent = user_agent
        self.auth_url = auth_url

    def get_access_token(self, email, password):
        s = robobrowser.RoboBrowser(user_agent=self.user_agent, parser="lxml")
        s.open(self.auth_url)

        f = s.get_form()
        f["pass"] = password
        f["email"] = email
        s.submit_form(f)
        f = s.get_form()

        if f.submit_fields.get('__CONFIRM__'):
            s.submit_form(f, submit=f.submit_fields['__CONFIRM__'])
        else:
            raise Exception(
                "Couldn't find the continue button. Maybe you supplied the wrong login credentials? Or maybe Facebook is asking a security question?")
        access_token = re.search(r"access_token=([\w\d]+)", s.response.content.decode()).groups()[0]

        return access_token
