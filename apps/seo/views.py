"""Machine-readable surfaces: robots.txt, llms.txt, llms-full.txt.

All three are rendered dynamically so they reflect live content and the SEO
settings (AI-crawler policy, discourage-search). They're served at the site root,
outside the i18n URL prefixes.
"""

from __future__ import annotations

from django.http import HttpResponse
from django.urls import reverse
from django.utils.html import strip_tags

from apps.content.models import Page, Post
from apps.core.models import SiteSettings

from .constants import AI_CRAWLER_USER_AGENTS
from .models import SeoSettings

# Private areas that should never be crawled regardless of policy.
DISALLOWED_PATHS = ["/dashboard/", "/accounts/", "/admin/", "/library/"]

# Cap how many items the llms.txt files list/inline, to bound response size.
LLMS_MAX_ITEMS = 100


def _text(content: str, content_type: str = "text/plain; charset=utf-8") -> HttpResponse:
    return HttpResponse(content, content_type=content_type)


def robots_txt(request) -> HttpResponse:
    seo = SeoSettings.load()
    lines: list[str] = []

    if seo.discourage_search:
        # Staging / private: ask everyone to stay out, advertise no sitemap.
        lines += ["User-agent: *", "Disallow: /"]
        return _text("\n".join(lines) + "\n")

    lines += ["User-agent: *"]
    lines += [f"Disallow: {path}" for path in DISALLOWED_PATHS]
    lines += [""]

    # Explicit, grouped policy for the answer-engine crawlers. A named-bot group
    # overrides the "*" group entirely, so repeat the private-path Disallows here
    # (most-specific rule wins, so "Allow: /" still opens the rest of the site).
    lines += ["# AI answer-engine crawlers"]
    for agent in AI_CRAWLER_USER_AGENTS:
        lines += [f"User-agent: {agent}"]
        if seo.allow_ai_crawlers:
            lines += [f"Disallow: {path}" for path in DISALLOWED_PATHS]
            lines += ["Allow: /", ""]
        else:
            lines += ["Disallow: /", ""]

    lines += [f"Sitemap: {request.build_absolute_uri(reverse('sitemap'))}"]
    return _text("\n".join(lines) + "\n")


def _published_pages():
    return Page.objects.published().filter(noindex=False)[:LLMS_MAX_ITEMS]


def _published_posts():
    return Post.objects.published().filter(noindex=False).select_related("author")[:LLMS_MAX_ITEMS]


def llms_txt(request) -> HttpResponse:
    """A concise, link-first index of the site (see llmstxt.org)."""
    site = SiteSettings.load()
    seo = SeoSettings.load()
    summary = (seo.default_meta_description or site.tagline or "").strip()

    out: list[str] = [f"# {site.site_name}"]
    if summary:
        out += ["", f"> {summary}"]

    pages = list(_published_pages())
    if pages:
        out += ["", "## Pages"]
        for page in pages:
            url = request.build_absolute_uri(page.get_absolute_url())
            desc = page.seo_description()
            out += [f"- [{page.seo_title()}]({url})" + (f": {desc}" if desc else "")]

    posts = list(_published_posts())
    if posts:
        out += ["", "## Blog"]
        for post in posts:
            url = request.build_absolute_uri(post.get_absolute_url())
            desc = post.seo_description()
            out += [f"- [{post.seo_title()}]({url})" + (f": {desc}" if desc else "")]

    return _text("\n".join(out) + "\n", content_type="text/markdown; charset=utf-8")


def llms_full_txt(request) -> HttpResponse:
    """Like llms.txt but with the full, plain-text content inlined for direct reading."""
    site = SiteSettings.load()
    seo = SeoSettings.load()
    summary = (seo.default_meta_description or site.tagline or "").strip()

    out: list[str] = [f"# {site.site_name}"]
    if summary:
        out += ["", f"> {summary}"]

    def section(title: str, items) -> None:
        rendered = list(items)
        if not rendered:
            return
        out.append("")
        out.append(f"# {title}")
        for obj in rendered:
            url = request.build_absolute_uri(obj.get_absolute_url())
            out.extend(["", f"## {obj.seo_title()}", f"URL: {url}", ""])
            body = strip_tags(getattr(obj, "body", "") or "").strip()
            out.append(body if body else obj.seo_description())

    section("Pages", _published_pages())
    section("Blog", _published_posts())

    return _text("\n".join(out) + "\n", content_type="text/markdown; charset=utf-8")
