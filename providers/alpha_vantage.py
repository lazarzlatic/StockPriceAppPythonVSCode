"""
providers/alpha_vantage.py
==========================
Alpha Vantage data provider.
Fetches daily time series and company overview via the official Alpha Vantage API.

Limits: 25 requests/day, 5 requests/minute on the free tier.
Docs:   https://www.alphavantage.co/documentation/
"""

import os
import requests
from .base import FIXED_DATES, find_closest_date, calculate_change

BASE_URL = 'https://www.alphavantage.co/query'


def fetch(ticker: str) -> dict:
    """
    Fetch stock data from Alpha Vantage TIME_SERIES_DAILY endpoint.

    Returns a standardised result dictionary (see providers/__init__.py for schema).
    Raises ValueError for invalid tickers, rate limits, or missing data.
    """
    api_key = os.environ.get('ALPHA_VANTAGE_API_KEY', '')
    if not api_key:
        raise ValueError(
            'Alpha Vantage API key not configured. '
            'Please add ALPHA_VANTAGE_API_KEY to your .env file.'
        )

    print(f'📊 Alpha Vantage: fetching {ticker}')

    # ── Daily time series ────────────────────────────────────────────────────
    response = requests.get(BASE_URL, params={
        'function':   'TIME_SERIES_DAILY',
        'symbol':     ticker.upper(),
        'outputsize': 'full',
        'apikey':     api_key,
    }, timeout=15)
    response.raise_for_status()
    data = response.json()

    if 'Error Message' in data:
        raise ValueError(f'Invalid ticker symbol: {ticker}')
    if 'Note' in data or 'Information' in data:
        raise ValueError(
            'Alpha Vantage API rate limit reached (25 calls/day). '
            'Please try again later or switch to Yahoo Finance.'
        )
    if 'Time Series (Daily)' not in data:
        raise ValueError(f'No data found for ticker: {ticker}')

    time_series = data['Time Series (Daily)']
    sorted_dates = sorted(time_series.keys(), reverse=True)

    if not sorted_dates:
        raise ValueError(f'No trading data available for: {ticker}')

    # ── Current price ────────────────────────────────────────────────────────
    current_date = sorted_dates[0]
    current_price = float(time_series[current_date]['4. close'])
    open_price    = float(time_series[current_date]['1. open'])
    daily_change, daily_change_percent = calculate_change(current_price, open_price)

    # ── Company name (best-effort — costs 1 extra API call) ──────────────────
    company_name = ticker.upper()
    try:
        overview = requests.get(BASE_URL, params={
            'function': 'OVERVIEW',
            'symbol':   ticker.upper(),
            'apikey':   api_key,
        }, timeout=10).json()
        company_name = overview.get('Name', ticker.upper()) or ticker.upper()
    except Exception:
        pass  # Name is optional; fall back to ticker symbol

    # ── Build result ─────────────────────────────────────────────────────────
    result = {
        'symbol':        ticker.upper(),
        'name':          company_name,
        'price':         current_price,
        'currency':      'USD',
        'change':        daily_change,
        'changePercent': daily_change_percent,
        'timestamp':     current_date,
    }

    # 5 trading days ago
    if len(sorted_dates) > 5:
        price_5 = float(time_series[sorted_dates[5]]['4. close'])
        change_5, pct_5 = calculate_change(current_price, price_5)
        result.update({'price5DaysAgo': price_5, 'change5Days': change_5, 'changePercent5Days': pct_5})

    # 30 trading days ago
    if len(sorted_dates) > 30:
        price_30 = float(time_series[sorted_dates[30]]['4. close'])
        change_30, pct_30 = calculate_change(current_price, price_30)
        result.update({'price30DaysAgo': price_30, 'change30Days': change_30, 'changePercent30Days': pct_30})

    # Fixed dates
    all_dates = list(time_series.keys())
    for key, label, change_key, pct_key, price_key in [
        ('april1_2025',    'priceApril1_2025',    'changeApril1',    'changePercentApril1',    'priceApril1_2025'),
        ('october1_2025',  'priceOctober1_2025',  'changeOctober1',  'changePercentOctober1',  'priceOctober1_2025'),
        ('december1_2025', 'priceDecember1_2025', 'changeDecember1', 'changePercentDecember1', 'priceDecember1_2025'),
    ]:
        closest = find_closest_date(all_dates, FIXED_DATES[key])
        if closest:
            p = float(time_series[closest]['4. close'])
            c, pct = calculate_change(current_price, p)
            result[price_key]  = p
            result[change_key] = c
            result[pct_key]    = pct

    print(f'✅ Alpha Vantage: {ticker} = ${current_price}')
    return result
