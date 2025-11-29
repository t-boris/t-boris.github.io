# Info worth sharing (Jekyll + Chirpy)

Static blog for https://blog.tsekinovsky.me built on Jekyll 4.3 with the Chirpy theme, Disqus comments, Google Analytics, and a scheduled events pipeline that enriches `_data/events.json` and renders archives under `/events/archive/`.

## Features
- Responsive theme with TOC, RSS feed, SEO tags, light/dark switch, and PWA enabled.
- Events generator (Python) that fetches local happenings, writes `_data/events.json`, and produces daily markdown archives in `_event_archives/`.
- GitHub Pages deployment from `gh-pages` driven by GitHub Actions; `CNAME` set for the custom domain.
- Posts, categories, tags, and tab pages with pinned/hidden support and math/Mermaid opt-ins.

## Repository layout
- `_config.yml` - global site config (theme, analytics, comments, pagination).
- `_data/` - shared data (assets config, contacts, share links, locales, events.json).
- `_includes/` and `_layouts/` - template overrides (head, sidebar, home, custom layouts).
- `_posts/` - blog posts `YYYY-MM-DD-title.md`; `_tabs/` - nav pages; `assets/` - images and favicons.
- `_plugins/posts-lastmod-hook.rb` - stamps posts with last_modified_at from Git history.
- `scripts/` - automation (events fetcher, Python requirements); `config/events.json` - fetcher settings.
- `_site/` - build output (ignored); `_event_archives/` - generated event day pages.

## Prerequisites
- Ruby 3.3 with Bundler.
- Python 3.11 for the events pipeline (optional unless updating events).
- Git and a working `make`-less shell (commands below use Bundler directly).

## Setup
```bash
bundle install
# optional: events pipeline deps
python -m pip install --upgrade pip
pip install -r scripts/requirements.txt
```

## Local development
- Serve with live reload: `bundle exec jekyll serve --livereload` then open http://127.0.0.1:4000
- Build only: `bundle exec jekyll build` (writes `_site/`).
- Sanity check: `bundle exec jekyll doctor`.

## Content authoring
- Posts: create `_posts/YYYY-MM-DD-title.md` with front matter `layout: post`, `title`, `date`, `categories`, `tags`; optional `pin`, `hidden`, `excerpt`, `image`, `math`, `mermaid`, `comments`.
- Tabs: create `_tabs/name.md` with `layout: page`, `title`, `order`, and optional `icon`.
- Assets: place under `assets/`; keep file names lower-case with dashes; optimize large images before committing.
- Do not edit `_site/` or generated `_event_archives/` by hand.

## Events data pipeline
- Config: `config/events.json` (location, city rotation, query templates, categories).
- Secrets: set `XAI_API_KEY` in your environment or GitHub Secrets.
- Run locally: `XAI_API_KEY=... python scripts/fetch_events.py` (updates `_data/events.json` and `_event_archives/`).
- Output: per-day markdown archives and JSON keyed by discovery date; keep ISO dates (`YYYY-MM-DD`).

## Deployment and CI
- `.github/workflows/github-pages.yml` builds with Ruby 3.3, runs `bundle exec jekyll build`, and publishes `_site/` to `gh-pages` on pushes to `main` or after a successful events run.
- `.github/workflows/generate-events.yml` runs nightly at 03:00 UTC or on demand; commits updated `_data/events.json` and `_event_archives/` back to `main` if changes exist.
- `.github/workflows/test-events.yml` is a manual dry-run for the events fetcher without committing.

## Troubleshooting
- Build fails: rerun `bundle exec jekyll build` locally and check for Liquid/YAML errors.
- Missing styles/scripts: ensure CDN URLs in `_data/assets/cross_origin.yml` are reachable.
- Events issues: confirm `XAI_API_KEY` is set and JSON output is valid (use `python -m json.tool _data/events.json`).

## Contributing and further docs
- See `AGENTS.md` for contributor guidelines and workflow tips.
- `ARCHITECTURE.md` (Russian) covers the theme stack, layouts, and performance notes.
