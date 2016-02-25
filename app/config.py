import os


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'asdasd23ěšěůdsfčřé99090;;;#`'
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # currency
    YAHOO_BASE_URL = 'https://download.finance.yahoo.com/d/quotes.csv?f=sl1&s={0}'
    REFERENCE_CURRENCY = 'EUR'
    SYMBOLS_PER_REQUEST = 50

    # question generation
    QUESTIONS_PER_RUN = 10
    TOLERANCE = "?"


class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True

config = DevelopmentConfig()