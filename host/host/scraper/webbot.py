import re
import time
import sys
import robobrowser
import logging
import json
import uuid

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.common.keys import Keys

from host.host.db_api import create_user
from host.host.scraper.browser import get_browser
from host.host.utils import images as utils_images
from host.host.utils.aws import s3_put_png

from typing import Dict

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


class WebBot:
    def __init__(self, email: str, password: str, push_to_server: bool = False,
                 sleep_multiplier: int = 1, browser: str = "firefox", debug: bool = False):
        self.email = email
        self.password = password
        self.push_to_server = push_to_server
        self.browser = get_browser(browser)
        self.debug = debug
        self.sleep_multiplier = sleep_multiplier

        self.browser.get('https://tinder.com/app/login')

    def get_bio(self) -> str:

        time.sleep(2)

        try:
            elem = self.browser.find_element_by_css_selector('body')
            elem.send_keys(Keys.ARROW_UP)
            time.sleep(2 * self.sleep_multiplier)

            profile_card = self.browser.find_element_by_xpath("//div[contains(@class, 'BreakWord')]")

            # idk why tinder did this but it's dumb text is broken up into spans
            outer_div = profile_card.find_element_by_css_selector("div")
            text_elements = outer_div.find_elements_by_css_selector("span")

            profile_text = ""

            for text_element in text_elements:
                if text_element.text is not None:
                    profile_text += text_element.text

            return profile_text

        except Exception as e:
            logger.error("Bio not found: {}".format(e))

            return None

    def _get_content_element(self):
        return self.browser.find_element_by_id("content")

    def _get_button_by_aria_label(self, aria_label: str):
        return self.browser.find_element_by_xpath("//button[@aria-label='{}']".format(aria_label))

    def swipe_left(self):
        e = self._get_button_by_aria_label("Nope")
        self.browser.execute_script("arguments[0].click();", e)

    def swipe_right(self):
        e = self._get_button_by_aria_label("Like")
        self.browser.execute_script("arguments[0].click();", e)

    def login_facebook(self):
        time.sleep(5 * self.sleep_multiplier)

        try:
            # more_options_button = self.browser.find_element_by_partial_link_text("More Options")
            # more_options_button.click()
            time.sleep(2)
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

    def get_image_url(self, style: str):
        """

        :param element:
        :return:
        """
        # style = element.get("style")
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
            self.browser.switch_to.active_element.send_keys(Keys.ARROW_UP)
            for _ in range(9):
                time.sleep(1)
                container = self.browser.find_element_by_class_name("react-swipeable-view-container")
                image_element = container.find_element_by_xpath("//div[@aria-hidden='false']")
                image_element = image_element.find_element_by_xpath("//div[@aria-label='Profile slider']")
                style = image_element.get_attribute("style")

                image_url = self.get_image_url(style)

                if image_url not in user_image_urls and image_url != "":
                    user_image_urls.append(image_url)
                self.browser.switch_to.active_element.send_keys(Keys.SPACE)

        except NoSuchElementException as e:
            self.browser.switch_to.active_element.send_keys(Keys.ARROW_DOWN)

            logger.error("An image url could not be found!\n{}".format(e))

            return None
        self.browser.switch_to.active_element.send_keys(Keys.ARROW_DOWN)

        return user_image_urls

    def get_next_image_button(self):
        return self.browser.find_elements_by_xpath("//*[contains(@class, 'pageButton')]")

    def get_next_button_element(self):
        return self.browser.find_element_by_xpath("//button[@aria-label='Next']")

    def get_enable_notifications_not_interested(self):
        # return self.browser.find_element_by_xpath("//button[@aria-label='Not interested']")

        try:
            return WebDriverWait(self.browser, 25).until(
                EC.presence_of_element_located((By.XPATH, "//button[@aria-label='Not interested']"))
            )
        except TimeoutException as time_out_e:
            logging.error(time_out_e)
        except NoSuchElementException as e:
            logging.error("NoSuchElementException!")
            logging.error(e)
        except WebDriverException as e:
            logging.error(e)
        except Exception as e:
            logging.error(e)

    def get_matches_element(self):
        return self.browser.find_elements_by_xpath("//button[@aria-label='Not interested']")

    def get_location_allow_button(self):
        try:
            return WebDriverWait(self.browser, 25).until(
                EC.presence_of_element_located((By.XPATH, "//button[@aria-label='Allow']"))
            )
        except TimeoutException as time_out_e:
            logging.error(time_out_e)
        except NoSuchElementException as e:
            logging.error("NoSuchElementException!")
            logging.error(e)
        except WebDriverException as e:
            logging.error(e)
        except Exception as e:
            logging.error(e)

        # return self.browser.find_element_by_xpath("//button[@aria-label='Allow']")

    def check_for_match_popup(self):
        try:
            time.sleep(7 * self.sleep_multiplier)
            self.browser.find_element_by_xpath("//a[@aria-current='page']").click()

            return True
        except (NoSuchElementException, WebDriverException) as e:  # If didnt match with person then go on
            if isinstance(e, WebDriverException):
                logging.error(e)

            return False


def get_tinder_user_image_dir(images_file_path, tinder_user_name):
    return '{}/{}'.format(images_file_path, tinder_user_name)


class AutoSwiper(WebBot):
    def __init__(self, *args, **kwargs):
        super(AutoSwiper, self).__init__(*args, **kwargs)

        self.profile_count = 0

    def restart_check(self):
        if self.debug:
            response = input("There was an error, press any button to continue")

        sys.stdout.write('Error: Elements are gone restarting...')
        sys.stdout.flush()

        input("Press Enter to restart...")

        self.browser.close()

    def start(self, location: Dict):
        self.login_facebook()

        location_button = self.get_location_allow_button()
        location_button.click()

        not_interested_button = self.get_enable_notifications_not_interested()
        not_interested_button.click()

        bio_checker = BioCheck()

        while True:
            time.sleep(2 * self.sleep_multiplier)
            bio_text = self.get_bio()

            if bio_text is None:
                bio_text = None

            if self.push_to_server:
                name, age = self.get_name_age()
                image_urls = self.get_all_image_urls()

                if image_urls is not None:
                    image_objects = []

                    for i, image_url in enumerate(image_urls):
                        image = utils_images.get_image(image_url)
                        file_name = str(uuid.uuid4())
                        key = s3_put_png(image, file_name)

                        image_objects.append({
                            "id": file_name,
                            "url": image_url,
                            "s3_name": key,
                            "image_number": i,
                            "legacy": False
                        })

                    user = {
                        "name": name,
                        "age": age,
                        "bio": bio_text,
                        "images": image_objects
                    }

                    user.update(location)

                    if name is not None and len(image_objects) > 0:
                        created = create_user(user)
                        if created:
                            self.profile_count += 1

                            log = 'Total Scraped: {} | Scraped {} with info: age: {} - ' \
                                  'has bio: {} - Image count: {}'.format(self.profile_count, name, age,
                                                                         bio_text is not None,
                                                                         len(image_objects))
                            print(log)
            time.sleep(2)
            if bio_text is not None and not bio_checker.check(bio_text):
                self.swipe_left()
            else:
                self.swipe_right()
            self.check_for_match_popup()


class BioCheck:
    def __init__(self, rules_file: str = "rules.json"):
        with open(rules_file, "r") as f:
            rules = json.load(f)

        left_keywords = rules.get("left")
        right_keywords = rules.get("right")

        if left_keywords is None:
            raise ValueError("The key \"left\" must be defined in the json file!")

        if right_keywords is None:
            raise ValueError("The key \"right\" must be defined in the json file!")

        regex_rules = dict()

        for key, values in rules.items():
            regex_rules[key] = re.compile("|".join(v for v in values))

        self.regex_rules = regex_rules

    def check(self, bio: str) -> bool:
        """
        Return False if any keywords appear in the "keywords"

        :param bio: a str of the profile bio
        """

        bio = bio.lower()

        if self.regex_rules["left"].match(bio):
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
