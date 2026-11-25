# URL Shortener with Analytics

A minimal Flask application that creates short links, redirects visitors, and counts clicks using SQLite.

## Requirements
- Python 3.10+
- Flask

## Run
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000. Use the local dashboard to create a link and inspect click counts.

## Notes
This is a development/demo service. Add authentication, rate limiting, abuse prevention, and HTTPS before deploying publicly. Links are stored in `shortener.db`.
