import os


class Config:
    EMAIL = os.getenv("EMAIL")
    PASSWORD = os.getenv("PASSWORD")
    DATABASE_URL = os.getenv("DATABASE_URL")
    APIURL = ""

    FACEBOOK_ID = os.getenv("FACEBOOK_ID")
    FACEBOOK_AUTH_TOKEN = os.getenv("FACEBOOK_AUTH_TOKEN")
    MOBILE_USER_AGENT = os.getenv("MOBILE_USER_AGENT")
    AUTH_URL = os.getenv("AUTH_URL")
