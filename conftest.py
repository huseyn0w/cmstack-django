import pytest
from django.core.cache import cache


@pytest.fixture(autouse=True)
def _clear_cache():
    """Clear the (process-global) cache around every test.

    SiteSettings and the active theme are cached; without this, a value set in
    one test could leak into another and make the suite order-dependent.
    """
    cache.clear()
    yield
    cache.clear()
