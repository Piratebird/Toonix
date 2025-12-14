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

# doujin tag id
DOUJIN_TAG_ID = "b13b2a48-c720-44a9-9c77-39c9979373fb"

# ---- FUNCTIONS ---- #

# search manga

"""
title -> a string containing the manga title (query).
limit -> integer controlling how many results to request [default value of 10].

NOTE might add a timeout later on such as search_manga(title,limit=10,timeout=6).
"""


def search_manga(title, limit=10):
    """
    search manga by name/title.
    returns a list of manga results.
    """
    url = f"{BASE_URL}/manga"
    params = {
        "title": title,
        "limit": limit,
        "includes[]": ["cover_art", "tags"],
        "excludedTags[]": [DOUJIN_TAG_ID],
        "contentRating[]": ["safe", "suggestive"],
    }

    r = requests.get(url, params=params)
    if r.status_code != 200:
        return []

    data = r.json().get("data", [])
    safe_results = []
    for m in data:
        if is_doujin(m) or looks_like_doujin(m):
            continue
        safe_results.append(m)

    return safe_results


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

"""
Returns a valid cover image ID+filename for a manga.
Instead of building url_for here, Flask will do it in app.py
"""


def get_manga_cover(manga):
    relationships = manga.get("relationships") or []
    for rel in relationships:
        if rel.get("type") == "cover_art":
            file_name = rel.get("attributes", {}).get("fileName")
            if file_name:
                return (manga["id"], file_name)
    return None


# get chapter(s) list
def get_manga_chapters(manga_id, lang="en"):
    """
    returns all available chapters for a manga in the chosen language.

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

"""
returns a list of page-image URLs for a chapter.

MangaDex uses a decentralized CDN system called 'at-home' server ,
[endpoint used to fetch image files for a chapter].
"""


def get_chapter_images(chapter_id):
    cache_file = os.path.join(CHAPTER_CACHE_DIR, f"{chapter_id}.json")
    chapter_data = None

    # Try to load cache first
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r") as f:
                chapter_data = json.load(f)
        except (OSError, json.JSONDecodeError):
            chapter_data = None

    # Fetch from server if cache is missing or invalid
    if not chapter_data:
        url = f"{BASE_URL}/at-home/server/{chapter_id}"
        r = requests.get(url)
        if r.status_code != 200:
            print(f"[ERROR] Chapter {chapter_id} not found on server")
            return None
        chapter_data = r.json()
        # save cache
        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(chapter_data, f, ensure_ascii=False, indent=2)
        except OSError:
            pass

    # Extract URLs
    base = chapter_data.get("baseUrl")
    info = chapter_data.get("chapter")
    if not base or not info:
        return None

    chapter_hash = info.get("hash")
    pages = info.get("data", [])
    if not chapter_hash or not pages:
        return None

    images = [f"{base}/data/{chapter_hash}/{page}" for page in pages]
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


def is_doujin(manga):
    for tag in manga["attributes"].get("tags", []):
        if tag["id"] == DOUJIN_TAG_ID:
            return True
    return False


def looks_like_doujin(manga):
    title = manga["attributes"].get("title", {})
    en = title.get("en", "").lower()
    return "doujin" in en
