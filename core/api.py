# attempt for using the mangadex api "https://api.mangadex.org"

import requests
import os
import json

# ---- CONSTANTS AND DIRECTORIES -------#

BASE_URL = "https://api.mangadex.org"
UPLOADS_URL = "https://uploads.mangadex.org"

CACHE_DIR = "data/cache/manga_metada"
CHAPTER_CAHCE_DIR = "data/cache/chapters"
DOWNLOADS_DIR = "data/downloads"


# ---- CREATE NEEDED DIRECTORIES -------#
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
        # parse the json data into python readable shenanigans (dict & lists)
        return r.json().get("data", [])
    return []


# fetch manga metadata (cached)


def fetch_manga_local(manga_id):
    """
    fetch a manga by ID [used id since it's unique identifier].
    uses local cache if found otherwise requests from MangaDex.
    """

    # make the file name based on the manga id (json file btw)
    cache_file = os.path.join(CACHE_DIR, f"{manga_id}.json")

    # load from cache if it exists
    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            return json.load(f)

    # fetch from the mangadex api if the there's no cache
    url = f"{BASE_URL}/manga/{manga_id}"
    params = {"includes[]": "cover_art"}
    r = requests.get(url, params=params)

    if r.status_code == 200:  # http -> ok (success)
        data = r.json().get("data")

        if data:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensures_ascii=False, indent=2)
            return data
    return None


# get cover image url
def get_manga_cover():
    pass


# get chapter(s) list
def get_manga_chapters():
    pass
