import httplib
import urllib
from lib import PUSHOVER_USER, PUSHOVER_TOKEN


class Pushover(object):
    user = PUSHOVER_USER
    token = PUSHOVER_TOKEN

    @classmethod
    def send(cls, title, message):
        if not cls._has_valid_token():
            return
        conn = httplib.HTTPSConnection("api.pushover.net:443")
        conn.request(
            "POST", "/1/messages.json",
            urllib.urlencode({
                    "token": cls.token,
                    "user":  cls.user,
                    "title": title,
                    "message": message,
            }),
            {"Content-type": "application/x-www-form-urlencoded"})
        return

    @staticmethod
    def _has_valid_token():
        return bool(Pushover.user and Pushover.token)
