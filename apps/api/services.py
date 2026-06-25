"""API services — the data the API viewsets expose, via content repositories.

Viewsets stay at the HTTP boundary and call these; no ``Model.objects`` here.
"""

from __future__ import annotations

from django.db import connection
from django.db.models import QuerySet

from apps.content.repositories import (
    CategoryRepository,
    PageRepository,
    PostRepository,
    ServiceRepository,
    TagRepository,
)


def published_posts() -> QuerySet:
    return PostRepository.published()


def published_pages() -> QuerySet:
    return PageRepository.published()


def published_services() -> QuerySet:
    return ServiceRepository.published()


def all_categories() -> QuerySet:
    return CategoryRepository.with_post_counts()


def all_tags() -> QuerySet:
    return TagRepository.with_post_counts()


def database_ok() -> bool:
    """True if a trivial query against the database succeeds (readiness probe)."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:  # pragma: no cover - exercised only when the DB is down
        return False
    return True
