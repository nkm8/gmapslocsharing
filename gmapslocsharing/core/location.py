from cachetools import TTLCache, cached
from datetime import datetime
import logging
import brotli
import json
import re

log = logging.getLogger(__name__)

STATE_CACHING_SECONDS = 30
STATE_CACHE = TTLCache(maxsize=1, ttl=STATE_CACHING_SECONDS)

class Location:

    def __init__(self, session, path, config, person, debug):

        self.debug = debug
        self.raw_output = None
        self.clean_people = []
        self.person_class = person
        self.people = []
        self.session = session
        self.config = config

        self.debug_folder = path / 'debug'
        self.debug_file = self.debug_folder / 'raw_output_debug'

        self.headers = {'authority': self.config['header_authority'],
                        'accept-language': 'en-US,en;q=0.9',
                        'accept-encoding': 'gzip, deflate, br',
                        'accept': 'application/json, text/plain, */*',
                        'referer': self.config['header_referer'],
                        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'}
        self.payload = {'authuser': 1,
                        'hl': 'en',
                        'gl': 'us',
                        'authuser': 1,
                        'pb': '!1e1!2m2!1sp-PDW8CZOKj_0gKPorqABQ!7e81!3m2!1s107699590211062977112!2s'}

        self.debug_file.touch(mode=0o660)

    def query_data(self):

        try:
            log.info('Query Data - Requesting location data.')
            response = self.session.get(self.config['sharing_url'], params=self.payload, headers=self.headers)
            log.info('Query Data - Decompressing and decoding response.')
            self.raw_output = brotli.decompress(response.content).decode('utf-8')

            if self.debug:
                self.debug_output('raw query output', self.raw_output)

            return True

        except Exception as e:
            log.error('Query Data Error - {}'.format(e))
            return False

    def clean_data(self):

        self.clean_people = []

        raw_output = self.raw_output.split('[[')[2:]

        keep = {
                1: 'id',
                3: 'photo',
                5: 'full_name',
                8: 'gps',
                9: 'address',
                11: 'country',
                21: 'first_name',
                22: 'battery'
                }

        p = 0
        people = {}
        rm = []
        for person in raw_output:
            i = 0
            proceed = True
            name = person.split('"')[5].split(',')[0]
            people.update({p:{}})
            for line in person.split('"'):
                line = [_.strip('[]\n') for _ in line.split(',')]
                if i in keep.keys() and proceed:
                    try:
                        if i == 1:
                            people[p].update({keep[i]: int(line[0])})
                        if i == 8:
                            people[p].update({'gps':{}})
                            people[p]['gps'].update({'latitude': line[4]})
                            people[p]['gps'].update({'longitude': line[3]})
                            people[p].update({'last_seen': int(line[5])/1000})
                            people[p]['gps'].update({'accuracy': int(line[6])})
                        elif i == 9:
                            people[p].update({'address': ''.join(line[:])})
                        elif i == 22:
                            people[p].update({'battery':{}})
                            battery = [int(_) for _ in line[7:9]]
                            if battery[0] == 0:
                                people[p]['battery'].update({   'charging': False,
                                                                'percent': battery[1]})
                            elif battery[0] == 1:
                                people[p]['battery'].update({   'charging': True,
                                                                'percent': battery[1]})
                        else:
                            people[p].update({keep[i]: line[0]})
                    except Exception as e:
                        log.error('Clean Data - Bad data from user {}: {}'.format(name, e))
                        log.error('Clean Data - Dumping raw data for user to debug file.')
                        if self.debug:
                            self.debug_output('Clean Data', raw_output[p])
                        if p not in rm:
                            rm.append(p)
                        proceed = False
                i += 1
            p += 1

        for x in rm:
            del people[x]

        if len(people.keys()) == 0:
            log.error('Zero valid output from query.')
            return False
        else:
            for person in people.keys():
                self.clean_people.append(people[person])
            return True

    def create_people(self):

        Person = self.person_class
        people = self.clean_people

        log.info('Create People - Clearing previously stored data.')
        self.people = []

        log.info('Create People - Converting location data into Person object.')
        for person in people:
            self.people.append(Person(person))

        log.info('Create People - Created {} people.'.format(len(self.people)))

    # TODO: should probably modify cache duration based on refresh interval
    # from configuration.yaml. consideration would be if ttl is shorter than
    # refresh interval possibly? need to dig into this functionality a bit more
    # to determine best course of action.
    @cached(STATE_CACHE)
    def update(self):

        try:
            log.info('Performing data query.')
            if self.query_data():
                log.info('Performing data cleanup.')
                if self.clean_data():
                    log.info('Creating people.')
                    self.create_people()
        except Exception as e:
            log.error('Update error - {}'.format(e))

    def debug_output(self, origin, debug):

        timestamp = datetime.now().strftime('%Y-%m-%d - %H:%M:%S')

        with open(self.debug_file, mode='a') as f:
            f.write('\n\n[{}][{}]:\n\n'.format(timestamp, origin))
            f.write(debug)
