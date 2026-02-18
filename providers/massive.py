"""
providers/massive.py
====================
Massive.com data provider (Polygon.io-compatible REST API).

Uses two endpoints (both available on free tier):
  - /v2/aggs/ticker/{ticker}/range/1/day/{from}/{to}  → current price + full history
  - /v3/reference/tickers/{ticker}                    → company name

Current price  = most recent bar's close (results[0].c)
Daily change   = difference between most recent close and previous day's close
Authentication: apiKey query parameter
Free tier available at https://massive.com
Docs: https://massive.com/docs/rest/quickstart
"""

import os
import requests
from datetime import datetime, timedelta
from .base import FIXED_DATES, find_closest_date, calculate_change

BASE_URL = 'https://api.massive.com'


def fetch(ticker: str) -> dict:
    """
    Fetch stock data from Massive.com.

    Returns a standardised result dictionary (see providers/__init__.py for schema).
    Raises ValueError for invalid tickers, missing API key, or missing data.
    """
    api_key = os.environ.get('MASSIVE_API_KEY', '')
    if not api_key:
        raise ValueError(
            'Massive API key not configured. '
            'Please add MASSIVE_API_KEY to your .env file. '
            'Get a free key at https://massive.com'
        )

    print(f'📊 Massive: fetching {ticker}')

    # ── Historical daily bars — current price + 1 year of history ────────────
    from_date = (datetime.now() - timedelta(days=400)).strftime('%Y-%m-%d')
    to_date   = datetime.now().strftime('%Y-%m-%d')

    agg_resp = requests.get(
        f'{BASE_URL}/v2/aggs/ticker/{ticker.upper()}/range/1/day/{from_date}/{to_date}',
        params={'adjusted': 'true', 'sort': 'desc', 'limit': 400, 'apiKey': api_key},
        timeout=15,
    )
    agg_resp.raise_for_status()
    agg_data = agg_resp.json()

    if agg_data.get('status') == 'ERROR':
        raise ValueError(f'Massive API error for ticker: {ticker}')

    results = agg_data.get('results', [])
    if not results:
        raise ValueError(f'No data found for ticker: {ticker}')

    # results sorted desc (newest first); each bar: t=ms timestamp, c=close, o=open
    current_bar  = results[0]
    current_price = round(float(current_bar['c']), 2)
    current_date  = datetime.fromtimestamp(current_bar['t'] / 1000).strftime('%Y-%m-%d')

    # Daily change vs previous day's close
    if len(results) > 1:
        prev_close = round(float(results[1]['c']), 2)
        daily_change, daily_change_pct = calculate_change(current_price, prev_close)
    else:
        daily_change, daily_change_pct = 0.0, 0.0

    # ── Company name — ticker reference (best-effort) ─────────────────────────
    company_name = ticker.upper()
    try:
        ref_resp = requests.get(
            f'{BASE_URL}/v3/reference/tickers/{ticker.upper()}',
            params={'apiKey': api_key},
            timeout=10,
        )
        ref_data = ref_resp.json()
        company_name = ref_data.get('results', {}).get('name', ticker.upper()) or ticker.upper()
    except Exception:
        pass  # Name is optional

    # ── Build date → price map for historical lookups ─────────────────────────
    date_price_map = {
        datetime.fromtimestamp(bar['t'] / 1000).strftime('%Y-%m-%d'): round(float(bar['c']), 2)
        for bar in results
        if bar.get('c') is not None
    }
    all_dates = list(date_price_map.keys())

    # ── Build result ──────────────────────────────────────────────────────────
    result = {
        'symbol':        ticker.upper(),
        'name':          company_name,
        'price':         current_price,
        'currency':      'USD',
        'change':        daily_change,
        'changePercent': daily_change_pct,
        'timestamp':     current_date,
    }

    # 5 trading days ago
    if len(results) > 5:
        price_5 = round(float(results[5]['c']), 2)
        change_5, pct_5 = calculate_change(current_price, price_5)
        result.update({'price5DaysAgo': price_5, 'change5Days': change_5, 'changePercent5Days': pct_5})

    # 30 trading days ago
    if len(results) > 30:
        price_30 = round(float(results[30]['c']), 2)
        change_30, pct_30 = calculate_change(current_price, price_30)
        result.update({'price30DaysAgo': price_30, 'change30Days': change_30, 'changePercent30Days': pct_30})

    # Fixed dates
    for key, price_key, change_key, pct_key in [
        ('april1_2025',    'priceApril1_2025',    'changeApril1',    'changePercentApril1'),
        ('october1_2025',  'priceOctober1_2025',  'changeOctober1',  'changePercentOctober1'),
        ('december1_2025', 'priceDecember1_2025', 'changeDecember1', 'changePercentDecember1'),
    ]:
        closest = find_closest_date(all_dates, FIXED_DATES[key])
        if closest:
            p = date_price_map[closest]
            c, pct = calculate_change(current_price, p)
            result[price_key]  = p
            result[change_key] = c
            result[pct_key]    = pct

    print(f'✅ Massive: {ticker} = ${current_price}')
    return result
