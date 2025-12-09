# Toonix

A simple Flask project for managing comics.

## Project Structure

```
toonix/ # Project root
├── app.py # Main Flask app
├── database.db # SQLite database (auto-created or prefilled)
├── requirements.txt # Python dependencies (Flask, requests, etc.)
├── templates/ # HTML templates
│ ├── base.html # Base template with Bootstrap + navbar
│ ├── home.html # Home page (featured comics)
│ ├── genre.html # Genre listing page
│ ├── comic_detail.html # Comic detail page with chapters
│ └── add_comic.html # Form to add new comics manually
├── static/ # Static files
│ ├── css/
│ │ └── style.css # Custom CSS
│ ├── js/
│ │ └── script.js # Custom JS / jQuery
│ └── images/ # Default images / cover placeholders
├── core/ # Python modules for logic / API
│ ├── models.py # Database models / ORM
│ ├── api.py # API import logic (MangaDex or dummy)
│ └── utils.py # Helper functions
├── data/ # Optional: store local comics, covers, etc.
└── uploads/ # Uploaded images or comics (PDF/CBZ)
```
