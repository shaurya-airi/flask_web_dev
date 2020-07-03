import os
class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or b'w\xdeDl\x91C\x1f\xa0\x93\x9f\x92}\x06\x08\xfc\n'
    MONGODB_SETTING = {'db': 'UTA_Enrollment'}
