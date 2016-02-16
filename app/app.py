import os

from flask import Flask, request, render_template

from .api import api
from .extensions import db
from .config import DevelopmentConfig

# For import *
__all__ = ['create_app']

DEFAULT_BLUEPRINTS = (
    api,
)


def create_app(config=os.environ['APP_SETTINGS'], app_name='Math', blueprints=None):
    """Create a Flask app.
    :param blueprints:
    :param app_name:
    :param config:
    """

    if blueprints is None:
        blueprints = DEFAULT_BLUEPRINTS

    app = Flask(app_name)
    configure_app(app, config)
    configure_blueprints(app, blueprints)

    return app


def configure_app(app, config=None):
    """Different ways of configurations.
    :param app: app instance
    :param config: app configuration
    """

    if config:
        app.config.from_object(DevelopmentConfig)


def configure_extensions(app):
    # flask-sqlalchemy
    db.init_app(app)


def configure_blueprints(app, blueprints):
    """Configure blueprints in views."""

    for blueprint in blueprints:
        app.register_blueprint(blueprint)