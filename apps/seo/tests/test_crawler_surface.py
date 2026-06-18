"""sitemap.xml, robots.txt and llms.txt / llms-full.txt."""

import pytest
from django.contrib.auth import get_user_model

from apps.content.models import Page, Post, Status
from apps.seo.models import SeoSettings

User = get_user_model()
pytestmark = pytest.mark.django_db


@pytest.fixture
def author():
    return User.objects.create_user(username="writer")


@pytest.fixture
def content(author):
    live = Post.objects.create(
        title="Live Post",
        excerpt="Live summary.",
        body="<p>Live body text.</p>",
        author=author,
        status=Status.PUBLISHED,
    )
    Post.objects.create(title="Draft Post", author=author)  # excluded everywhere
    page = Page.objects.create(
        title="About", body="<p>About body.</p>", author=author, status=Status.PUBLISHED
    )
    return live, page


# --------------------------------------------------------------------------- #
# sitemap.xml
# --------------------------------------------------------------------------- #
def test_sitemap_lists_published_excludes_drafts(client, content):
    live, page = content
    xml = client.get("/sitemap.xml").content.decode()
    assert client.get("/sitemap.xml").status_code == 200
    assert f"/blog/{live.slug}/" in xml
    assert f"/pages/{page.slug}/" in xml
    assert "draft-post" not in xml


def test_sitemap_has_hreflang_alternates(client, content):
    xml = client.get("/sitemap.xml").content.decode()
    assert "xhtml:link" in xml
    assert 'hreflang="de"' in xml
    assert 'hreflang="en"' in xml


def test_sitemap_excludes_noindex(client, author):
    Post.objects.create(title="Hidden", author=author, status=Status.PUBLISHED, noindex=True)
    xml = client.get("/sitemap.xml").content.decode()
    assert "hidden" not in xml


# --------------------------------------------------------------------------- #
# robots.txt
# --------------------------------------------------------------------------- #
def test_robots_default_policy(client):
    resp = client.get("/robots.txt")
    assert resp.status_code == 200
    assert resp["Content-Type"].startswith("text/plain")
    body = resp.content.decode()
    assert "Disallow: /dashboard/" in body
    assert "User-agent: GPTBot" in body
    assert "User-agent: ClaudeBot" in body
    assert "User-agent: PerplexityBot" in body
    assert "Sitemap: http://testserver/sitemap.xml" in body
    ai_section = body.split("# AI", 1)[1]
    # AI crawlers allowed, but still steered away from private areas.
    assert "Disallow: /\n" not in ai_section
    assert "Disallow: /dashboard/" in ai_section
    assert "Allow: /" in ai_section


def test_robots_blocks_ai_when_disabled(client):
    seo = SeoSettings.load()
    seo.allow_ai_crawlers = False
    seo.save()
    body = client.get("/robots.txt").content.decode()
    ai_section = body.split("# AI", 1)[1]
    assert "Disallow: /" in ai_section
    assert "Allow: /" not in ai_section


def test_robots_discourage_search_blocks_everyone(client):
    seo = SeoSettings.load()
    seo.discourage_search = True
    seo.save()
    body = client.get("/robots.txt").content.decode()
    assert "User-agent: *" in body
    assert "Disallow: /" in body
    assert "GPTBot" not in body  # short-circuited policy
    assert "Sitemap:" not in body


# --------------------------------------------------------------------------- #
# llms.txt / llms-full.txt
# --------------------------------------------------------------------------- #
def test_llms_txt_indexes_published_content(client, content):
    live, page = content
    body = client.get("/llms.txt").content.decode()
    assert body.startswith("# ")  # site name heading
    assert f"/blog/{live.slug}/" in body
    assert "Live Post" in body
    assert "About" in body
    assert "Draft Post" not in body


def test_llms_full_txt_includes_body_text(client, content):
    body = client.get("/llms-full.txt").content.decode()
    assert "Live body text." in body
    assert "About body." in body
    # HTML is stripped, not raw.
    assert "<p>" not in body
