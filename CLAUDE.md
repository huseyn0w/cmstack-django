# CLAUDE.md

This file guides Claude Code (CLI / VSCode extension) when working in this repository.

## Project

DjangoPress is an open-source, WordPress-style CMS built on Python/Django. Goal: same
core capabilities as WordPress, but lighter, faster, SEO-first, and easy to read,
understand, and extend. It is a commercial/open project that will be demoed publicly,
so code quality, security, and a clean demo matter.

Reference implementation by the same author (Laravel, study for feature parity, not for
code style): https://github.com/huseyn0w/Laravella-CMS

## Stack (confirm in the roadmap before building; deviate only with a stated reason)

- Python 3.12, Django 5.x
- PostgreSQL (default). Keep all DB access ORM-level and DB-agnostic so MySQL works for
  shared hosting.
- Tailwind CSS 3 + Alpine.js, bundled with Vite (django-vite).
- Auth/social login: django-allauth. Multilingual: django-parler or django-modeltranslation.
- Spam: django-recaptcha (v3). Rich text editor: a maintained, sanitized editor.
- Tests: pytest + pytest-django. Lint/format: ruff + black. Types: mypy where it pays off.
- Local infra: Docker + docker compose. Prod: gunicorn + nginx + whitenoise on VPS;
  a separate guide for shared hosting (Hostinger / Passenger / cPanel).

## Architecture conventions

- Idiomatic Django, organized as focused Django apps (e.g. accounts, content, media,
  themes, plugins, seo, comments, search, api/mcp). One app = one bounded concern.
- Thin views, logic in model methods and small service functions. Add a repository or
  service layer only where it removes real duplication — do not add it speculatively.
- Themes: swappable template sets resolved at runtime. Plugins: extension points via
  Django signals / a small hook registry, not arbitrary code injection.
- SEO/GEO is a first-class app: Open Graph, JSON-LD, sitemap.xml, robots.txt, hreflang.

## Commands (keep this section updated as the project grows)

- Dev up: `docker compose up`
- Migrate: `docker compose exec web python manage.py migrate`
- Seed demo data: `docker compose exec web python manage.py seed_demo`
- Tests: `docker compose exec web pytest` (single test: `pytest path::test_name`)
- Lint/format: `ruff check .` and `black .`
- Frontend build: `cd frontend && npm run build` (watch: `npm run dev`)
- Lint locally without Docker: `pytest`, `ruff check .`, `black .` from a venv with
  `requirements/dev.txt` installed.

## Project structure (as built)

- `config/` — Django project. Settings are split under `config/settings/`:
  `base.py` (shared, reads env via django-environ), `dev.py`, `prod.py` (hardened),
  `test.py` (in-memory SQLite, no external services). `urls.py`, `wsgi.py`, `asgi.py`.
- `apps/` — one Django app per bounded concern. App label is `apps.<name>`
  (e.g. `apps.core`). New apps: set `name = "apps.<name>"` in their `AppConfig`.
  - `apps.accounts` — custom user (`AUTH_USER_MODEL = "accounts.User"`), roles as
    Django Groups, granular permissions. Default roles + their permissions are
    defined in `apps/accounts/roles.py` and synced idempotently on every
    `post_migrate` (`apps/accounts/signals.py`); the map may reference permissions
    from models that don't exist yet (they're assigned once those phases land).
    Auth/social login via django-allauth, mounted at `/accounts/`.
  - `apps.content` — posts, pages, categories (hierarchical), tags, and per-type
    revisions. Rich-text bodies are sanitized server-side with nh3 on every save
    (`apps/content/utils.py`); templates render bodies with `|safe` because they
    were cleaned at write time — keep it that way. `publish_post` is a custom
    permission; published querysets via `Model.objects.published()`. Content is
    editable through the interim Django admin until the Phase 5 panel exists.
  - `apps.media` — media library. `MediaAsset` stores files plus extracted metadata
    and a Pillow thumbnail (built on first save). Uploads validated in `forms.py`
    (allowed types in `constants.py`; SVG rejected as an XSS vector). Browse/upload/
    delete views are permission-gated (`media.*_mediaasset`). Files served at
    `/media/` (Django in dev, web server in prod).
- `frontend/` — Vite + Tailwind + Alpine source; builds to `frontend/dist`
  (with `.vite/manifest.json`), wired into templates via `django-vite`.
- `templates/` — project-level base templates (`base.html`).
- `docker/` — `entrypoint.sh` (waits for DB, migrates, then runs the CMD).
- `requirements/` — `base.txt`, `dev.txt`, `prod.txt`.

Settings selection: `DJANGO_SETTINGS_MODULE` chooses dev/prod; pytest pins
`config.settings.test` via `--ds` so the container's env var can't override it.
Frontend assets: in dev with the Vite server, set `DJANGO_VITE_DEV_MODE=True` for HMR;
otherwise built assets are served from the manifest (the docker compose default).

## Working rules

- Run tests and ruff after every change; a change is not done until both pass.
- Only make changes directly requested or clearly necessary. Do not add extra files,
  abstractions, or configurability that was not asked for.
- Never commit secrets; all config via environment variables (.env, with .env.example).
- Keep README.md and this file current when commands, stack, or structure change.
- Communicate with the user in English.
