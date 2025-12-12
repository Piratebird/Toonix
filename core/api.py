# attempt for using the mangadex api "https://api.mangadex.org"

import requests
import os
import json

# ---- CONSTANTS AND DIRECTORIES -------#

BASE_URL = "https://api.mangadex.org"
UPLOADS_URL = "https://uploads.mangadex.org"

CACHE_DIR = "data/cache/manga_metadata"
CHAPTER_CACHE_DIR = "data/cache/chapters"
DOWNLOADS_DIR = "data/downloads"


# ---- CREATE NEEDED DIRECTORIES -------#
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(CHAPTER_CACHE_DIR, exist_ok=True)
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

# search manga

"""
title -> a string containing the manga title (query).
limit -> interger controlling how many results to request [default value of 10].

NOTE might add a timeout later on such as search_manga(title,limit=10,timeout=6).
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
    manga -> python dictionary that is passed.
    fileName -> actual image file name.
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
    returns all avilable chapters for a manga in the chosem language.

    currently this only limits to 500 chapter per request later on will have a better implementation.
    """

    # the endpoint for querying chapters
    url = f"{BASE_URL}/manga/{manga_id}/feed"
    params = {
        "translatedLanguage[]": lang,
        # sort in an ascending order 1,2,3...etc
        "order[chapter]": "asc",
        "limit": 500,
        "includes[]": ["scanlation_group", "user"],
    }

    r = requests.get(url, params=params)
    if r.status_code == 200:
        return r.json().get("data", [])
    return []


# get chapter image urls


def get_chapter_images(chapter_id):
    """
    returns a list of page-image URLs for a chapter.

    MangaDex uses a decenteralized CDN system called 'at-home' server ,
    [endpoint used ti fetch image files for a chapter].
    """
    # path to local cache for this chapter's at-home response
    cache_file = os.path.join(CHAPTER_CACHE_DIR, f"{chapter_id}.json")

    # load from cache if we have cached data
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r") as f:
                chapter_data = json.load(f)
        except (OSError, json.JSONDecodeError):
            # corrupted cache ignore it and refetch
            chapter_data = None
    else:
        # fetch from Mangadex at-home server info for this chapter
        url = f"{BASE_URL}/at-home/server/{chapter_id}"
        r = requests.get(url)

        # if the requests fails return None
        if r.status_code != 200:
            return None

        # parse the JSON response into python objects
        chapter_data = r.json()

        # cache it for next time usage
        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(chapter_data, f, indent=2, ensure_ascii=False)
        except OSError:
            # caching failed, but we still have chapter_data
            pass

    # extract required fields
    base = chapter_data["baseUrl"]  # base url of at-home server -> starts the URL
    info = chapter_data["chapter"]  # chapter metadata -> holds hash and pages
    chapter_hash = info.get(
        "hash"
    )  # folder name for this chapter -> needed to build path
    pages = info.get("data", [])  # list of filenames -> needed to fetch each image

    if not base or not chapter_hash or not pages:
        return None

    # empty list to store final URLs
    images = []

    # loop through every filename in the list of pages
    for filename in pages:
        # build the full image URl for this page and append it to the list of images
        image_url = f"{base}/data/{chapter_hash}/{filename}"
        images.append(image_url)

    return images


# download chapter locally
def download_chapter(chapter_id):
    """
    downloads all pages of a chapter into /data/downloads
    """

    images = get_chapter_images(chapter_id)

    if not images:
        return False

    chapter_dir = os.path.join(DOWNLOADS_DIR, str(chapter_id))
    os.makedirs(chapter_dir, exist_ok=True)

    for i, img in enumerate(images):
        r = requests.get(img)
        if r.status_code == 200:
            file_path = os.path.join(chapter_dir, f"page_{i+1}.jpg")
            # wb -> writing for pdfs images...etc
            with open(file_path, "wb") as f:
                f.write(r.content)

    return True
