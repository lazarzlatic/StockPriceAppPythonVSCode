"""
providers/fmp.py
================
Financial Modeling Prep (FMP) data provider.

Uses two stable API endpoints:
  - /stable/quote                    → current price, daily change, company name
  - /stable/historical-price-eod/light → 1-year daily closing prices

Free tier: 250 requests/day
Docs: https://site.financialmodelingprep.com/developer/docs
"""

import os
import requests
from datetime import datetime, timedelta
from .base import FIXED_DATES, find_closest_date, calculate_change

BASE_URL = 'https://financialmodelingprep.com/stable'


def fetch(ticker: str) -> dict:
    """
    Fetch stock data from Financial Modeling Prep.

    Returns a standardised result dictionary (see providers/__init__.py for schema).
    Raises ValueError for invalid tickers, missing API key, or missing data.
    """
    api_key = os.environ.get('FMP_API_KEY', '')
    if not api_key:
        raise ValueError(
            'FMP API key not configured. '
            'Please add FMP_API_KEY to your .env file. '
            'Get a free key at https://financialmodelingprep.com/register'
        )

    print(f'📊 FMP: fetching {ticker}')

    # ── Quote — current price, daily change, company name ────────────────────
    quote_resp = requests.get(
        f'{BASE_URL}/quote',
        params={'symbol': ticker.upper(), 'apikey': api_key},
        timeout=15,
    )
    quote_resp.raise_for_status()
    quote_data = quote_resp.json()

    if not quote_data or (isinstance(quote_data, dict) and quote_data.get('error')):
        raise ValueError(f'No data found for ticker: {ticker}')

    if isinstance(quote_data, list) and len(quote_data) == 0:
        raise ValueError(f'Ticker "{ticker}" not found on FMP.')

    quote = quote_data[0] if isinstance(quote_data, list) else quote_data

    current_price     = round(float(quote['price']), 2)
    daily_change      = round(float(quote.get('change', 0) or 0), 2)
    daily_change_pct  = round(float(quote.get('changesPercentage', 0) or 0), 2)
    company_name      = quote.get('name') or ticker.upper()

    # ── Historical EOD light — 1 year of daily closing prices ────────────────
    from_date = (datetime.now() - timedelta(days=400)).strftime('%Y-%m-%d')

    hist_resp = requests.get(
        f'{BASE_URL}/historical-price-eod/light',
        params={'symbol': ticker.upper(), 'from': from_date, 'apikey': api_key},
        timeout=15,
    )
    hist_resp.raise_for_status()
    hist_raw = hist_resp.json()

    # Response may be a flat list or wrapped {"historical": [...]}
    if isinstance(hist_raw, dict):
        historical = hist_raw.get('historical', [])
    else:
        historical = hist_raw or []

    if not historical:
        raise ValueError(f'No historical data available for: {ticker}')

    # Sort newest-first; build date → price map
    historical.sort(key=lambda x: x['date'], reverse=True)
    date_price_map = {
        entry['date']: round(float(entry['price']), 2)
        for entry in historical
        if entry.get('price') is not None
    }
    all_dates     = list(date_price_map.keys())
    latest_date   = all_dates[0] if all_dates else datetime.now().strftime('%Y-%m-%d')

    # ── Build result ──────────────────────────────────────────────────────────
    result = {
        'symbol':        ticker.upper(),
        'name':          company_name,
        'price':         current_price,
        'currency':      'USD',
        'change':        daily_change,
        'changePercent': daily_change_pct,
        'timestamp':     latest_date,
    }

    # 5 trading days ago
    if len(historical) > 5:
        price_5 = round(float(historical[5]['price']), 2)
        change_5, pct_5 = calculate_change(current_price, price_5)
        result.update({'price5DaysAgo': price_5, 'change5Days': change_5, 'changePercent5Days': pct_5})

    # 30 trading days ago
    if len(historical) > 30:
        price_30 = round(float(historical[30]['price']), 2)
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

    print(f'✅ FMP: {ticker} = ${current_price}')
    return result
