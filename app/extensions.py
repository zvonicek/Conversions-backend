from flask.ext.compress import Compress
from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug.contrib.cache import FileSystemCache

db = SQLAlchemy()

cache = FileSystemCache(cache_dir='.')

compress = Compress()