# lifted shamelessly from locationsharinglib

class Person:

    def __init__(self, data):

        self.data = data

    def __str__(self):
        text = (u'Full name        :{}'.format(self.data['full_name']),
                u'Nickname         :{}'.format(self.data['first_name']),
                u'Current location :{}'.format(self.data['address']),
                u'Latitute         :{}'.format(self.data['gps']['latitude']),
                u'Longitude        :{}'.format(self.data['gps']['longitude']),
                u'Datetime         :{}'.format(self.data['last_seen']),
                u'Charging         :{}'.format(self.data['battery']['charging']),
                u'Battery %        :{}'.format(self.data['battery']['percent']),
                u'Accuracy         :{}'.format(self.data['gps']['accuracy']))
        return '\n'.join(text)

    @property
    def id(self):
        """The internal google id of the account"""
        return self.data['id'] or self.data['full_name']

    @property
    def picture_url(self):
        """The url of the person's avatar"""
        return self.data['photo']

    @property
    def full_name(self):
        """The full name of the user as set in google"""
        return self.data['full_name']

    @property
    def nickname(self):
        """The nickname as set in google"""
        # fix for when two first names
        if len(self.data['first_name'].split()) > 1:
            self.data['first_name'] = self.data['first_name'].split()[0]
        return self.data['first_name']

    @property
    def latitude(self):
        """The latitude of the person's current location"""
        return self.data['gps']['latitude']

    @property
    def longitude(self):
        """The longitude of the person's current location"""
        return self.data['gps']['longitude']

    @property
    def timestamp(self):
        """The timestamp of the location retrieval"""
        return self.data['last_seen']

    @property
    def datetime(self):
        """A datetime representation of the location retrieval"""
        return datetime.fromtimestamp(self.data['last_seen'] / 1000)

    @property
    def address(self):
        """The address as reported by google for the current location"""
        return self.data['address']

    @property
    def country_code(self):
        """The location's country code"""
        return self.data['country']

    @property
    def accuracy(self):
        """The accuracy of the gps"""
        return self.data['gps']['accuracy']

    @property
    def charging(self):
        """Whether or not the user's device is charging"""
        return self.data['battery']['charging']

    @property
    def battery_level(self):
        """The battery level of the user's device"""
        return self.data['battery']['percent']
