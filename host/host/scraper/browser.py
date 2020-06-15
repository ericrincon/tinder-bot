from selenium import webdriver
from selenium.webdriver import FirefoxProfile
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.options import Options

from webdriver_manager.chrome import ChromeDriverManager

from shutil import which

FIREFOXPATH = which("firefox")


def get_firefox(headless=False, *args, **kwargs):
    options = Options()
    options.binary = FIREFOXPATH

    if headless:
        options.add_argument("-headless")

    firefox_profile = FirefoxProfile()
    firefox_profile.set_preference("general.useragent.override",
                                   "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0")

    firefox_profile.set_preference("geo.prompt.testing", True)
    firefox_profile.set_preference("geo.prompt.testing.allow", True)
    binary = FirefoxBinary()

    return webdriver.Firefox(firefox_profile=firefox_profile, options=options, firefox_binary=binary)


def get_headless_firefox(*args, **kwargs):
    return get_firefox(headless=True, *args, **kwargs)


def get_chrome(headless=False, *args, **kwargs):
    chrome_options = webdriver.ChromeOptions()

    if headless:
        chrome_options.add_argument("--headless")

    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--enable-geolocation")

    return webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)


def get_headless_chrome(*args, **kwargs):
    return get_chrome(headless=True, *args, **kwargs)


_BROWSER_PROFILES = {
    "firefox": get_firefox,
    "chrome": get_chrome,
    "headless_firefox": get_headless_firefox,
    "headless_chrome": get_headless_chrome
}


def get_browser(browser, *args, **kwargs):
    if browser in _BROWSER_PROFILES:
        return _BROWSER_PROFILES[browser](*args, **kwargs)
    else:
        raise ValueError('Browser {} not defined!'.format(browser))
