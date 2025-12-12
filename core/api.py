# attempt for using the mangadex api "https://api.mangadex.org"

# import request
import os

# import json

# Constants and directories

BASE_URL = "https://api.mangadex.org"
UPLOADS_URL = "https://uploads.mangadex.org"

CACHE_DIR = "data/cache/manga_metada"
CHAPTER_CAHCE_DIR = "data/cache/chapters"
DOWNLOADS_DIR = "data/downloads"

# create needed direcctories
os.makedirs(CACHE_DIR, exits_ok=True)
os.makedirs(CHAPTER_CAHCE_DIR, exits_ok=True)
os.makedirs(DOWNLOADS_DIR, exits_ok=True)
