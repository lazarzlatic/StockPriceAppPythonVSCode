"""
providers/yahoo_finance.py
==========================
Yahoo Finance data provider.
Fetches 1-year daily chart data via the unofficial Yahoo Finance chart API.

No API key required. Requests are made server-side to bypass browser CORS restrictions.
Docs: https://query2.finance.yahoo.com/v8/finance/chart/<SYMBOL>
"""

import requests
from datetime import datetime
from .base import FIXED_DATES, find_closest_date, calculate_change

BASE_URL = 'https://query2.finance.yahoo.com/v8/finance/chart'

_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
}


def fetch(ticker: str) -> dict:
    """
    Fetch stock data from the Yahoo Finance chart endpoint.

    Returns a standardised result dictionary (see providers/__init__.py for schema).
    Raises ValueError for invalid tickers or missing data.
    """
    print(f'📊 Yahoo Finance: fetching {ticker}')

    response = requests.get(
        f'{BASE_URL}/{ticker.upper()}',
        params={'range': '1y', 'interval': '1d'},
        headers=_HEADERS,
        timeout=15,
    )
    response.raise_for_status()
    data = response.json()

    chart = data.get('chart', {})
    if chart.get('error'):
        raise ValueError(f"Yahoo Finance error: {chart['error'].get('description', 'Unknown error')}")

    result_data = chart.get('result')
    if not result_data:
        raise ValueError(f'No data found for ticker: {ticker}')

    result_item = result_data[0]
    meta       = result_item.get('meta', {})
    timestamps = result_item.get('timestamp', [])
    quotes     = result_item.get('indicators', {}).get('quote', [{}])[0]
    closes     = quotes.get('close', [])
    opens      = quotes.get('open', [])

    # Drop entries with no close price
    valid_data = [
        (ts, c, o)
        for ts, c, o in zip(timestamps, closes, opens)
        if c is not None
    ]

    if not valid_data:
        raise ValueError(f'No valid price data for: {ticker}')

    # ── Current price ────────────────────────────────────────────────────────
    latest_ts, latest_close, latest_open = valid_data[-1]
    current_price = round(latest_close, 2)
    current_date  = datetime.fromtimestamp(latest_ts).strftime('%Y-%m-%d')
    open_price    = latest_open if latest_open else current_price
    daily_change, daily_change_percent = calculate_change(current_price, open_price)

    company_name = meta.get('longName') or meta.get('shortName') or ticker.upper()

    # ── Build result ─────────────────────────────────────────────────────────
    result = {
        'symbol':        ticker.upper(),
        'name':          company_name,
        'price':         current_price,
        'currency':      meta.get('currency', 'USD'),
        'change':        daily_change,
        'changePercent': daily_change_percent,
        'timestamp':     current_date,
    }

    # Build date → price map for historical lookups
    date_price_map = {
        datetime.fromtimestamp(ts).strftime('%Y-%m-%d'): round(c, 2)
        for ts, c, _ in valid_data
    }
    all_dates = list(date_price_map.keys())

    # 5 trading days ago
    if len(valid_data) > 5:
        price_5 = round(valid_data[-6][1], 2)
        change_5, pct_5 = calculate_change(current_price, price_5)
        result.update({'price5DaysAgo': price_5, 'change5Days': change_5, 'changePercent5Days': pct_5})

    # 30 trading days ago
    if len(valid_data) > 30:
        price_30 = round(valid_data[-31][1], 2)
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

    print(f'✅ Yahoo Finance: {ticker} = ${current_price}')
    return result
