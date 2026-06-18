"""Answer-engine / AI crawler user agents.

These are the bots that feed ChatGPT, Claude, Perplexity, Google AI Overviews and
the Common Crawl corpus. The robots.txt view either explicitly allows or disallows
them as a group, controlled by SeoSettings.allow_ai_crawlers.
"""

AI_CRAWLER_USER_AGENTS = [
    "GPTBot",  # OpenAI training crawler
    "OAI-SearchBot",  # OpenAI search index
    "ChatGPT-User",  # ChatGPT browsing on a user's behalf
    "ClaudeBot",  # Anthropic crawler
    "Claude-Web",  # Anthropic browsing
    "anthropic-ai",  # Anthropic (legacy)
    "PerplexityBot",  # Perplexity
    "Google-Extended",  # Google Gemini / Vertex training
    "CCBot",  # Common Crawl (feeds many LLMs)
    "Applebot-Extended",  # Apple Intelligence training
]
