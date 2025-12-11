# Toonix

A simple Flask project for managing comics.

## Project Structure

```
toonix/                      # Project root
├── app.py                   # Main Flask app (routes: home, signup, login, logout, guest, search, manga detail, genre)
├── requirements.txt         # Python dependencies (Flask, requests, Flask-Session, etc.)
├── database.db              # SQLite database for users
├── core/                    # Python modules for logic / API
│   ├── api.py               # MangaDex API + local caching functions
│   ├── db_management.py     # Database functions for users (connect, addUser, auth)
│   └── utils.py             # Helper functions (optional)
├── data/                    # Store cached manga JSON and other local data
│   ├── cache/               # Cached manga metadata (JSON)
│   └── uploads/             # Manually uploaded comics or images
├── static/                  # Static files for front-end
│   ├── css/
│   │   └── style.css        # Custom styles
│   ├── js/
│   │   └── script.js        # Custom JS / jQuery
│   └── images/
│       └── placeholder.png  # Default cover image placeholder
├── templates/               # HTML templates
│   ├── base.html            # Base template with navbar (login/signup/guest/search/genres)
│   ├── home.html            # Home page (featured manga + search form)
│   ├── signup.html          # Signup page
│   ├── login.html           # Login page
│   ├── manga_search.html    # Search results page
│   ├── comic_detail.html    # Manga/comic detail page (title, description, cover)
│   └── genre.html           # Genre listing page (cards with manga covers)
└── README.md                # Project description / instructions

```

## Installation

```bash
# Clone the repo
git clone https://github.com/Piratebird/Toonix.git
cd Toonix

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```
