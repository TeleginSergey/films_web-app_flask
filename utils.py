"""This module provides utility functions."""
import os

import requests
from dotenv import load_dotenv

import config

load_dotenv()

OK = 200

API_URL = 'https://api.kinopoisk.dev/v1.4/movie/search?page=1&limit=1&query='


def get_rating_movie(title):
    """
    Fetch movie rating data from an external API based on the movie title.

    Args:
        title (str): The title of the movie to search for.

    Returns:
        dict: A dictionary containing movie data if the request is successful.
        None: If the request is unsuccessful, None is returned and an error message is printed.
    """
    headers = {
        'accept': 'application/json',
        'X-API-KEY': os.getenv('KINOPOISK_API_TOKEN'),
    }
    response = requests.get(config.API_URL + title, headers=headers)
    if response.status_code == OK:
        return response.json()
