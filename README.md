# DjangoPress

An open-source, WordPress-style CMS built on Python/Django — lighter, faster, SEO-first,
and easy to read, understand, and extend.

> **Status:** Phases 1–4 complete (Foundation, Accounts, Content, Media). See the roadmap below.

## Stack

- Python 3.12, Django 5.1
- PostgreSQL (default; ORM kept DB-agnostic so MySQL works on shared hosting)
- Tailwind CSS 3 + Alpine.js, bundled with Vite via `django-vite`
- Auth + social login: django-allauth (username/email login + Google)
- Rich-text sanitization: nh3 (server-side, on every save)
- Tests: pytest + pytest-django · Lint/format: ruff + black · Types: mypy
- Local infra: Docker + docker compose · Prod: gunicorn + nginx + whitenoise

## Quick start (Docker)

```bash
cp .env.example .env          # adjust if you like; defaults work out of the box
docker compose up --build
```

Then open <http://localhost:8000> — you should see the styled DjangoPress landing page.
The web container waits for Postgres, runs migrations, and serves the app on port 8000.

## Local development (without Docker)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements/dev.txt

# Frontend assets (Tailwind + Alpine via Vite)
cd frontend && npm install && npm run build && cd ..

# Run against a local Postgres, or export DATABASE_URL
python manage.py migrate
python manage.py runserver
```

For live frontend reloads, run the Vite dev server and enable dev mode:

```bash
cd frontend && npm run dev           # serves on :5173 with HMR
# in .env: DJANGO_VITE_DEV_MODE=True
```

## Project layout

```
config/            # Django project: settings split (base/dev/prod/test), urls, wsgi/asgi
  settings/
apps/              # Django apps, one per bounded concern
  accounts/        # custom User, roles (Groups), permissions, allauth + Google
  content/         # posts, pages, categories, tags, revisions, sanitization
  media/           # media library: uploads, validation, thumbnails
  core/            # landing page + shared bits
frontend/          # Vite + Tailwind + Alpine source (builds to frontend/dist)
templates/         # project-level base templates
docker/            # entrypoint and container helpers
requirements/      # base / dev / prod dependency sets
```

## Common commands

| Task | Command |
| --- | --- |
| Dev up | `docker compose up` |
| Migrate | `docker compose exec web python manage.py migrate` |
| Create admin user | `docker compose exec web python manage.py createsuperuser` |
| Tests | `docker compose exec web pytest` (or `pytest` in a local venv) |
| Single test | `pytest apps/core/tests/test_home.py::test_home_status_ok` |
| Lint / format | `ruff check .` · `black .` |
| Frontend build | `cd frontend && npm run build` (watch: `npm run dev`) |

## Accounts, roles & permissions

Authentication is handled by [django-allauth](https://docs.allauth.org): users sign in
with username **or** email and password, or via Google (set `GOOGLE_CLIENT_ID` /
`GOOGLE_CLIENT_SECRET`). Auth pages live under `/accounts/` (`/accounts/login/`,
`/accounts/signup/`, …) and use a styled DjangoPress layout.

Roles are WordPress-style and implemented as Django **Groups**, kept in sync by a
`post_migrate` hook (`apps/accounts/signals.py`) from a single definition in
`apps/accounts/roles.py`:

| Role | Capabilities (grows as later phases add models) |
| --- | --- |
| Administrator | All content/media/comment permissions + manage users & settings |
| Editor | All content/media + comment moderation; no user/settings management |
| Author | Create / edit / publish own posts, upload media |
| Contributor | Draft posts only (no publish, no media) |
| Subscriber | Authenticated reader; default role for new signups |

Permissions are standard Django permissions, so `user.has_perm(...)`,
`@permission_required`, and `PermissionRequiredMixin` all work. The sync is idempotent
and only assigns permissions whose models exist, so the table fills in across phases.

## Content

The `content` app provides the core CMS data model:

- **Posts** — title, auto unique slug, author, excerpt, sanitized rich-text body,
  featured image, draft/published status, categories (M2M) and tags (M2M). Publishing
  stamps `published_at`; `Post.objects.published()` is the public queryset.
- **Pages** — standalone, optionally hierarchical (e.g. About, Contact).
- **Categories** (hierarchical) and **Tags**.
- **Revisions** — every save of a post/page snapshots a `PostRevision`/`PageRevision`.

**Security:** all rich-text bodies are sanitized server-side with
[nh3](https://nh3.readthedocs.io) on every save (`apps/content/utils.py`), so stored
HTML is always safe regardless of what the editor or request sends. Templates render
the body with `|safe` precisely because it was cleaned at write time.

Public URLs: `/blog/` (list), `/blog/<slug>/` (post), `/blog/category/<slug>/`,
`/blog/tag/<slug>/`, `/pages/<slug>/`. Drafts return 404 to anonymous visitors but are
previewable by users with `content.change_post` / `content.change_page`.

> Content is editable via the interim Django admin (`/admin/`) for now; the bespoke,
> WordPress-style admin panel (dashboard, WYSIWYG editor, media picker, menus, settings)
> is **Phase 5**. The Django admin here is developer scaffolding, not the final admin UX.

## Media library

The `media` app manages uploads (`apps/media/`):

- **`MediaAsset`** — stores the file plus extracted metadata (MIME type, size, image
  width/height) and an auto-generated **thumbnail** (Pillow, max 400×400). Metadata and
  thumbnail are computed on first save.
- **Upload validation** — allowed types are JPG, PNG, GIF, WebP, PDF, capped at 10 MB.
  **SVG is rejected by design** (it can carry embedded scripts → stored-XSS risk).
- **Permission-gated views** — `/library/` (browse grid), `/library/upload/`,
  `/library/<id>/delete/`, each behind `LoginRequiredMixin` + the matching
  `media.*_mediaasset` permission. Editors/Admins get full access; Authors can upload but
  not delete; Contributors have no media access.

Uploaded files live under `MEDIA_ROOT` and are served at `/media/` (by Django in dev, by
the web server / object storage in production). Interim management is also available in the
Django admin; the polished picker integrates with the post editor in Phase 5.

## Configuration

All configuration is via environment variables (see [.env.example](.env.example)); no
secrets are committed. `DJANGO_SETTINGS_MODULE` selects the settings module
(`config.settings.dev` or `config.settings.prod`); the test suite always uses
`config.settings.test` (in-memory SQLite, no external services).

## Roadmap

1. **Foundation** — Docker, Django skeleton, settings split, pytest, ruff/black, Tailwind+Vite ✅
2. **Accounts** — custom user, roles (Groups), granular permissions, allauth + Google login ✅
3. **Content** — posts, pages, categories, tags, revisions, server-side sanitized rich text ✅
4. **Media** — media library, validated uploads, Pillow thumbnails, permission-gated ✅
5. Custom admin panel
6. Theme system (swappable template sets)
7. Plugin/extension system (signals + hook registry)
8. **SEO/GEO** — Open Graph, JSON-LD entity/service schema, sitemap, robots.txt with
   AI-crawler policy, `llms.txt`, hreflang, multilingual, GEO-optimized page type
   (see [SEO & GEO](#seo--geo-generative-engine-optimization))
9. Comments, search, recaptcha spam protection
10. Public site rendering + the luxury frontend
11. AI integration — MCP server (FastMCP)
12. Production deployment (VPS + shared hosting) + demo seed data

## SEO & GEO (Generative Engine Optimization)

> **Status: planned for Phase 8.** This section documents the target so it isn't lost.

DjangoPress is **SEO-first and GEO-first**: the goal is not only to rank in Google but to
be **parsed, understood, and cited by AI answer engines** (ChatGPT, Claude, Gemini,
Perplexity, Google AI Overviews) so that when someone asks an assistant for a service you
offer, your site is surfaced as a recommendation.

Getting recommended by an AI engine has two halves. DjangoPress owns the first; the second
is strategy/off-site and is supported by tooling, not a single page:

**1. On-site — what DjangoPress will build (Phase 8), so every page is AI-ingestible:**

- **AI crawler access** — `robots.txt` that explicitly allows the answer-engine bots
  (`GPTBot`, `OAI-SearchBot`, `ClaudeBot`, `PerplexityBot`, `Google-Extended`, `CCBot`),
  configurable per site, plus a clean `sitemap.xml`.
- **`llms.txt` / `llms-full.txt`** — a concise, machine-readable index of the site and its
  key pages/services that LLMs can read directly (as the reference CMS already did).
- **Structured data (JSON-LD)** — `Organization`, `LocalBusiness`, `Service`, `Product`,
  `FAQPage`, `Article`, `BreadcrumbList`, `Person` (author/E-E-A-T). This is how engines
  extract *which services you provide* and attach them to your entity.
- **A GEO-optimized "Service" page type** — a first-class template that pairs a service
  description with `Service` + `FAQPage` schema, crisp definitional sentences, Q&A blocks,
  pricing/area-served fields, and citable facts — the format answer engines quote verbatim.
- **Semantic, fast, server-rendered HTML** — correct heading hierarchy, canonical URLs,
  Open Graph/Twitter cards, hreflang for multilingual, and quick first-byte (no JS needed
  to read content), because engines reward extractable, fast pages.
- **Citable content patterns** — clear answers near the top, stats, FAQs, last-updated
  dates, and author identity to build the trust signals engines weigh.

**2. Off-site — what actually earns the recommendation (strategy, not a page):**

AI engines recommend brands they encounter repeatedly on sources they trust (reviews,
directories, comparison articles, Reddit/forums, reputable publications). On-site GEO makes
you *eligible and quotable*; visibility comes from being cited across the open web for your
service + location. This is a content-and-outreach program, measured by checking whether the
assistants actually cite you — handled by a dedicated **SEO/GEO strategy** workflow that
audits a specific live site, measures baseline AI visibility, and returns a prioritized plan.

## License

See [LICENSE](LICENSE).
