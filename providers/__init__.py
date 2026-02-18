"""
providers/__init__.py
=====================
Provider registry for the Stock Price Check App.

To add a new data provider:
  1. Create providers/<provider_name>.py with a fetch(ticker: str) -> dict function
  2. Import it below and add one entry to REGISTRY
  3. No changes to app.py are needed

The URL slug (e.g. 'alpha-vantage') is used directly in the API route:
  GET /api/<provider>/<ticker>
"""

from .alpha_vantage import fetch as _fetch_alpha_vantage
from .yahoo_finance import fetch as _fetch_yahoo_finance
from .fmp import fetch as _fetch_fmp
from .massive import fetch as _fetch_massive

# Maps URL slug → fetch function
REGISTRY: dict = {
    'alpha-vantage': _fetch_alpha_vantage,
    'yahoo-finance': _fetch_yahoo_finance,
    'fmp':           _fetch_fmp,
    'massive':       _fetch_massive,
}


def get_provider(name: str):
    """Return the fetch function for the given provider slug, or None if unknown."""
    return REGISTRY.get(name)
