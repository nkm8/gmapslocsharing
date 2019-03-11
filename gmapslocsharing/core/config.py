class Configuration:

    def __init__(self, country='US'):

        self.config = self.db(country)
        self.list = ['US']

    def db(self, country):

        db = {'US': {
                    'cookie':   {
                                'header_referer': 'https://accounts.google.com',
                                'domain': '.goole.com',
                                'login_start':'https://accounts.google.com',
                                'login_success':'https://myaccount.google.com/?pli=1'
                                },
                    'location': {
                                'header_authority': 'www.google.com',
                                'header_referer': 'https://www.google.com',
                                'sharing_url':'https://www.google.com/maps/preview/locationsharing/read'
                                }
                    }
                }

        output = db[country]
        return output
