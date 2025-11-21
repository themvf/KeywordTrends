# Niche Research Streamlit App

A Streamlit app that researches a niche keyword across YouTube, Etsy, Instagram, and the broader web (via Firecrawl). It fetches platform data, extracts keywords, and surfaces cross-platform patterns.

## Tech stack
- Streamlit UI
- Firecrawl for web and Etsy extraction
- YouTube Data API v3
- Instagram Graph API
- SQLite via SQLModel/SQLAlchemy
- Analysis with pandas and scikit-learn

## Project layout
- `app/main.py` — Streamlit entrypoint with tabbed UI
- `app/config.py` — settings loader (env/Streamlit secrets)
- `app/firecrawl_client.py` — thin wrapper for Firecrawl
- `app/sources/` — adapters for YouTube, Etsy, Instagram, general web
- `app/analysis/` — keyword extraction and scoring
- `app/storage/` — DB engine, models, and caching helpers
- `app/ui/` — reusable Streamlit components and charts
- `.streamlit/config.toml` — Streamlit theme
- `.github/workflows/ci.yml` — lint/test workflow

## Setup
1) Create a virtual environment and install deps:
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2) Add secrets (do not commit):
- Locally: create `.env` with keys:
```
FIRECRAWL_API_KEY=...   # or FIRECRAWL_API as an alias
YOUTUBE_API_KEY=...
INSTAGRAM_TOKEN=...
INSTAGRAM_USER_ID=...   # required for IG hashtag search
ETSY_API_KEY=...   # optional
DATABASE_URL=sqlite:///./niche.db
```
- Streamlit Cloud: set the same keys in `secrets`.

3) Run the app:
```
streamlit run app/main.py
```

## Development roadmap (phases)
- Phase 0: skeleton (this commit) + config/DB wiring
- Phase 1: Firecrawl + Etsy adapter end-to-end + Etsy tab charts
- Phase 2: YouTube adapter + tab with views/recency charts
- Phase 3: Keyword insights (cross-platform TF-IDF + gap scores)
- Phase 4: Instagram adapter + tab
- Phase 5: History/cache + export + polish

## Testing
```
pytest
```
