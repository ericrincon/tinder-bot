import re
import time
import sys

from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium import webdriver

from selenium.webdriver.common.keys import Keys

from database.db.models.user import TinderUser, Image
from database.db import Session

from host.host.utils import files
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

from host.host.utils import images as utils_images


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
    def __init__(self, email, password, browser='firefox'):
        self.email = email
        self.password = password
        self.browser = get_browser(browser)

        self.browser.get('https://tinder.com/app/login')

    def get_bio(self):
        try:
            elem = self.browser.find_element_by_css_selector('body')
            elem.send_keys(Keys.ARROW_UP)
            time.sleep(2)
            profile_card = self.browser.find_element_by_xpath("//*[contains(@class, 'profileCard__bio')]")

            profile_text = profile_card.find_element_by_css_selector('span')

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
                "//*[contains(@class, 'profileCard__header__info')]")
            name_age = profilecard_header_info.find_element_by_xpath(
                "//*[contains(@class, 'My(2px)')]").text

            if name_age:
                split_name_age = name_age.split()

                if split_name_age and len(split_name_age) == 2:
                    name, age = split_name_age

                    name = name.replace(',', '').strip()
                    age = int(age.replace(',', '').strip())
        except NoSuchElementException as e:
            print(e)
            print('Could not find name age element!')

            return None, None

        return name, age

    def get_profile_expand(self):

        return self.browser.find_element_by_xpath("//*[contains(@class, 'recCard__openProfile')]")

    def get_profile_card_element(self):
        return self.browser.find_element_by_xpath("//*[contains(@class, 'profileCard')]")

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
        style = element.get_attribute("style")

        if style != "":

            url = style.split()[-1][5:]
            url = url[:len(url) - 3]

        else:
            url = ""

        return url

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
                time.sleep(2)

                # find a better way but this works for now...
                picture_elements.send_keys(Keys.SPACE)

                image_elements = picture_elements.find_elements_by_xpath(
                    "//*[contains(@class, 'profileCard__slider__img')]")

                image_urls = list(map(lambda element: self.get_image_url(element), image_elements))
                image_urls = list(filter(lambda url: url != "", image_urls))
                image_urls = list(filter(lambda url: url not in user_image_urls, image_urls))

                user_image_urls.extend(image_urls)

        except NoSuchElementException as e:
            print(e)
            print('An image url could not be found!')

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
        return self.browser.find_element_by_xpath("//button[@aria-label='Onboarding.great']")



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

        # next_button = self.get_next_button_element()
        # next_button.click()
        location_button = self.get_location_allow_button()
        location_button.click()


        # Enhanced messaging prompt
        # next_button = self.get_next_button_element()
        # next_button.click()
        # Find the share button and click it
        # time.sleep(3)
        # share_button = self.get_share_button()
        # share_button.click()

        time.sleep(5)
        not_interested_button = self.get_enable_notifications_not_interested()
        not_interested_button.click()

        bio_checker = BioCheck()
        profiles_scraped = 0

        while True:
            console_info = ''

            try:
                time.sleep(2)

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
                if name is None and age is None and bio_text is None:
                    sys.stdout.write('Error: Elements are gone restarting...')
                    sys.stdout.flush()

                    self.browser.close()

                    return

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
                else:
                    sys.stdout.write('Error: Elements are gone restarting...')
                    sys.stdout.flush()

                    self.browser.close()

                    return

                user = TinderUser(name=name, age=age, bio=bio_text,
                                  images=images)
                utils_images.download_images(images)

                session.add(user)
                session.commit()
                session.close()
                profiles_scraped += 1
                profile_add_info = '\nAdded {} of age {} with {} images\n'.format(name, age, len(images))
                console_info += profile_add_info

                nb_scarped_text = '\n{} profiles scraped'.format(profiles_scraped)

                console_info += nb_scarped_text

                sys.stdout.write(console_info)

                if not bio_checker.check(bio_text):
                    print('Shes not into hookups!')
                    self.swipe_left()
                else:
                    self.swipe_right()
            except StaleElementReferenceException as e:
                print(e)
                print('Elements are gone restarting...')
                self.browser.close()

                return


class BioCheck:
    def __init__(self):
        self.regex = [re.compile(r"not into hook ups|no hookups")]

    def check(self, bio):
        bio = bio.lower()
        for exp in self.regex:
            if exp.match(bio):
                return False
        return True
