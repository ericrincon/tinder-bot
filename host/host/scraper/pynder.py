import pynder

from config import Config

from pynder.session import Session
class PynderBot:
    """
    Bot that uses the pynder library for automating tasks
    """

    def __init__(self, facebook_id, facebook_auth_token):
        """
        :param facebook_id: the users Facebook ID (can be gotten pretty easily)
        :param facebook_auth_token: the auth token used for tinder (Note: this requires
        more work to get but there are built in functions for that :) )
        """
        self.session = Session(facebook_id=facebook_id,
                                      facebook_token=facebook_auth_token)
