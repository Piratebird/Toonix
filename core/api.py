# attempt for using the mangadex api "https://api.mangadex.org"

import requests
import os
import json

# ---- CONSTANTS AND DIRECTORIES -------#

BASE_URL = "https://api.mangadex.org"
UPLOADS_URL = "https://uploads.mangadex.org"

CACHE_DIR = "data/cache/manga_metadata"
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
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Warning: cache file {cache_file} is corrupted. Refetching...")

    # fetch from the mangadex api if the there's no cache or if it's corrupted
    url = f"{BASE_URL}/manga/{manga_id}"
    params = {"includes[]": "cover_art"}
    r = requests.get(url, params=params)

    if r.status_code == 200:  # http -> ok (success)
        # parse response JSON and get the data field
        data = r.json().get("data")

        if data:
            with open(cache_file, "w", encoding="utf-8") as f:
                # non ascii-characters are allowed
                json.dump(data, f, ensure_ascii=False, indent=2)
            return data
    return None


# get cover image url
def get_manga_cover(manga):
    """
    manga -> python dictionary that is passed
    fileName -> actual image file name
    build and return the cover image url.
    """

    covers = []
    # access the relationship key in the manga dictionary,
    # which contains all related objects (author,artist,cover-art....etc)
    for rel in manga.get("relationships", []):
        # filters only what has cover_art type
        if rel["type"] == "cover_art":
            # make a list for the covers url
            covers.append(rel)

    # check if at least one cover exist
    if covers:
        # take the first art object and access the attributes for the filename
        file_name = covers[0]["attributes"]["fileName"]
        # retrives the manga id which is used in the url
        manga_id = manga["id"]
        # 512.jpg suffix specifies the width to 512px
        return f"{UPLOADS_URL}/covers/{manga_id}/{file_name}.512.jpg"
    # if there's no cover art (object) return none
    return None


# get chapter(s) list
def get_manga_chapters(manga_id, lang="en"):
    """
    returns all avilable chapters for a manga in the chosem language

    currently this only limits to 500 chapter per request later on will have a better implementation
    """

    # the endpoint for querying chapters
    url = f"{BASE_URL}/chapter"
    params = {
        "manga": manga_id,
        "translatedLanguage[]": lang,
        # sort in an ascending order 1,2,3...etc
        "order[chapter]": "asc",
        "limit": 500,
    }

    r = requests.get(url, params=params)
    if r.status_code == 200:
        return r.json().get("data", [])
    return []


def get_chapter_images(chapter_id):
    pass


def download_chapter(chapter_id):
    pass
