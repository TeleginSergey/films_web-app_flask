"""
Movie Database Application.

This module sets up a Flask application for managing actors and films in a database.
It configures the application, initializes the database, and registers blueprints
for actor and film-related operations.
"""
import os

import dotenv

API_URL = 'https://api.kinopoisk.dev/v1.4/movie/search?page=1&limit=1&query='
dotenv.load_dotenv()


class Config:
    """
    Base configuration class.

    Attributes:
        SQLALCHEMY_DATABASE_URI (str): Database URI for the application.
        SQLALCHEMY_TRACK_MODIFICATIONS (bool): Flag to disable modification tracking.
    """

    PG_VARS = 'PG_HOST', 'PG_PORT', 'PG_USER', 'PG_PASSWORD', 'PG_DBNAME'
    credentials = {env_var: os.environ.get(env_var) for env_var in PG_VARS}
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DBNAME}'.format(**credentials)

    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestConfig(Config):
    """
    Testing configuration class.

    Attributes:
        TESTING (bool): Flag to enable testing mode.
        SQLALCHEMY_DATABASE_URI (str): In-memory SQLite database URI for testing.
    """

    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
