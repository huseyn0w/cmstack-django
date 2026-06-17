# syntax=docker/dockerfile:1

# --------------------------------------------------------------------------- #
# Stage 1 — build the frontend (Tailwind + Alpine) with Vite.
# Produces frontend/dist including .vite/manifest.json.
# --------------------------------------------------------------------------- #
FROM node:22-slim AS frontend
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend/ ./
# Tailwind scans ../templates, ../apps and ../themes, so those must be present.
COPY templates /app/templates
COPY apps /app/apps
COPY themes /app/themes
RUN npm run build

# --------------------------------------------------------------------------- #
# Stage 2 — Python runtime.
# --------------------------------------------------------------------------- #
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps: libpq for psycopg, plus build basics.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/ requirements/
ARG REQUIREMENTS=dev
RUN pip install --no-cache-dir -r requirements/${REQUIREMENTS}.txt

COPY . .

# Bring in the built frontend assets from the frontend stage.
COPY --from=frontend /app/frontend/dist ./frontend/dist

RUN chmod +x docker/entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["docker/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
