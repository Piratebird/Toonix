# attempt for using the mangadex api "https://api.mangadex.org"

import requests
import os
import json

# Constants and directories

BASE_URL = "https://api.mangadex.org"
UPLOADS_URL = "https://uploads.mangadex.org"

CACHE_DIR = "data/cache/manga_metada"
CHAPTER_CAHCE_DIR = "data/cache/chapters"
DOWNLOADS_DIR = "data/downloads"

# create needed direcctories
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(CHAPTER_CAHCE_DIR, exist_ok=True)
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

# search manga

"""
title -> a string containing the manga title (query)
limit -> interger controlling how many results to request [default value of 10]

NOTE might add a timeout later on such as search_manga(title,limit=10,timeout=6)
"""


def search_manga(title, limit=10):
    """
    search manga by name/title.
    returns a list of manga resutls.
    """
    url = f"{BASE_URL}/manga"
    params = {"title": title, "limit": limit, "includes[]": "cover_art"}

    r = requests.get(url, params=params)
    # send a get request with the set parameters
    if r.status_code == 200:  # success
        # parse the json data into python readable shenanigans
        return r.json().get("data", [])
    return []


# fetch manga metadata (cached)


def fetch_manga_local():
    pass


# get cover image url
def get_manga_cover():
    pass


# get chapter(s) list
def get_manga_chapters():
    pass
