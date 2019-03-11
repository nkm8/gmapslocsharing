from .core.config import Configuration
from .core.cookie import CookieMonster
from .core.location import Location
from .core.person import Person
from pathlib import Path as p
import logging
import re
import sys

log = logging.getLogger(__name__)

class GoogleMaps:

    def __init__(self, login, password, config_path, cookie_name, country, debug):

        path = p(config_path)
        cookie = path / p(cookie_name)

        self.config = Configuration()

        self.startup(login, password, country)

        self.cookie = CookieMonster(login = login,
                                    password = password,
                                    config = self.config['cookie'],
                                    path = path,
                                    cookie = cookie,
                                    resolution = '768x1024',
                                    debug = debug)

        self.location = Location(   session = self.cookie.session,
                                    path = path,
                                    config = self.config['location'],
                                    person = Person,
                                    debug = debug)

        self.cookie_check()

    def startup(self, login, password, country):

        log.info('Starting gmapslocsharing system check.')

        log.info('Validating login.')
        if re.match('^[a-zA-Z0-9].*[a-zA-Z0-9.-].*[a-zA-Z0-9].*\@[a-zA-Z0-9.-].*[a-zA-Z0-9].*\.[a-zA-Z]{2,}$', login):
            log.info('Login validated.')
        else:
            log.error('Login either not present or not valid.')
            self.exit()
        log.info('Checking for password.')

        if password:
            log.info('Password provided.')
        else:
            log.error('Password not provided.')
            self.exit()

        log.info('Checking country code.')
        if country and country in self.config.list:
            log.info('Country code config available. Enabling config for {}.'
                            .format(country))
            self.config = Configuration(country).config
        else:
            log.warning('Country config not provided or not available. Defaulting to US.')
            self.config = Configuration().config

    def cookie_check(self):

        log.info('Initiating Cookie Check.')
        if self.cookie.check():
            log.info('Cookie validated or successfully generated.')
        else:
            log.error('Cookie check or generation failed.')
            self.exit()

    def exit(self):
        sys.exit
