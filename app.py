"""
Stock Price Check App - Flask Backend
=====================================
Dual API support: Alpha Vantage + Yahoo Finance
"""

import os
import requests
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

ALPHA_VANTAGE_API_KEY = os.environ.get('ALPHA_VANTAGE_API_KEY', '')
ALPHA_VANTAGE_BASE_URL = 'https://www.alphavantage.co/query'
YAHOO_FINANCE_BASE_URL = 'https://query2.finance.yahoo.com/v8/finance/chart'

# Fixed dates to track
FIXED_DATES = {
    'april1_2025': '2025-04-01',
    'october1_2025': '2025-10-01',
    'december1_2025': '2025-12-01',
}


def find_closest_date(dates: list, target_date: str) -> str | None:
    """Find the closest trading day within 7 days of target_date."""
    target = datetime.strptime(target_date, '%Y-%m-%d')
    for delta in range(8):
        # Search forward then backward
        for direction in [1, -1]:
            candidate = target + timedelta(days=delta * direction)
            candidate_str = candidate.strftime('%Y-%m-%d')
            if candidate_str in dates:
                return candidate_str
    return None


def calculate_change(current: float, previous: float) -> tuple:
    """Calculate change amount and percentage change."""
    change = current - previous
    percent_change = (change / previous * 100) if previous != 0 else 0
    return round(change, 2), round(percent_change, 2)


def fetch_alpha_vantage(ticker: str) -> dict:
    """
    Fetch stock data from Alpha Vantage TIME_SERIES_DAILY endpoint.
    Returns a structured dictionary with current price and historical comparisons.
    """
    print(f'📊 Alpha Vantage: fetching {ticker}')

    params = {
        'function': 'TIME_SERIES_DAILY',
        'symbol': ticker.upper(),
        'outputsize': 'full',
        'apikey': ALPHA_VANTAGE_API_KEY,
    }

    response = requests.get(ALPHA_VANTAGE_BASE_URL, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()

    if 'Error Message' in data:
        raise ValueError(f"Invalid ticker symbol: {ticker}")
    if 'Note' in data:
        raise ValueError("Alpha Vantage API rate limit reached (25 calls/day). Please try again later or use Yahoo Finance.")
    if 'Information' in data:
        raise ValueError("Alpha Vantage API rate limit reached. Please try again later or use Yahoo Finance.")
    if 'Time Series (Daily)' not in data:
        raise ValueError(f"No data found for ticker: {ticker}")

    time_series = data['Time Series (Daily)']
    sorted_dates = sorted(time_series.keys(), reverse=True)

    if not sorted_dates:
        raise ValueError(f"No trading data available for: {ticker}")

    # Current price (most recent close)
    current_date = sorted_dates[0]
    current_price = float(time_series[current_date]['4. close'])
    open_price = float(time_series[current_date]['1. open'])
    daily_change, daily_change_percent = calculate_change(current_price, open_price)

    result = {
        'symbol': ticker.upper(),
        'price': current_price,
        'currency': 'USD',
        'change': daily_change,
        'changePercent': daily_change_percent,
        'timestamp': current_date,
    }

    # 5 trading days ago
    if len(sorted_dates) > 5:
        price_5_days = float(time_series[sorted_dates[5]]['4. close'])
        change_5, change_pct_5 = calculate_change(current_price, price_5_days)
        result['price5DaysAgo'] = price_5_days
        result['change5Days'] = change_5
        result['changePercent5Days'] = change_pct_5

    # 30 trading days ago
    if len(sorted_dates) > 30:
        price_30_days = float(time_series[sorted_dates[30]]['4. close'])
        change_30, change_pct_30 = calculate_change(current_price, price_30_days)
        result['price30DaysAgo'] = price_30_days
        result['change30Days'] = change_30
        result['changePercent30Days'] = change_pct_30

    # Fixed dates
    all_dates = list(time_series.keys())

    april_date = find_closest_date(all_dates, FIXED_DATES['april1_2025'])
    if april_date:
        price_april = float(time_series[april_date]['4. close'])
        change_a, change_pct_a = calculate_change(current_price, price_april)
        result['priceApril1_2025'] = price_april
        result['changeApril1'] = change_a
        result['changePercentApril1'] = change_pct_a

    october_date = find_closest_date(all_dates, FIXED_DATES['october1_2025'])
    if october_date:
        price_october = float(time_series[october_date]['4. close'])
        change_o, change_pct_o = calculate_change(current_price, price_october)
        result['priceOctober1_2025'] = price_october
        result['changeOctober1'] = change_o
        result['changePercentOctober1'] = change_pct_o

    december_date = find_closest_date(all_dates, FIXED_DATES['december1_2025'])
    if december_date:
        price_december = float(time_series[december_date]['4. close'])
        change_d, change_pct_d = calculate_change(current_price, price_december)
        result['priceDecember1_2025'] = price_december
        result['changeDecember1'] = change_d
        result['changePercentDecember1'] = change_pct_d

    print(f'✅ Alpha Vantage: {ticker} = ${current_price}')
    return result


def fetch_yahoo_finance(ticker: str) -> dict:
    """
    Fetch stock data from Yahoo Finance API.
    Returns a structured dictionary with current price and historical comparisons.
    """
    print(f'📊 Yahoo Finance: fetching {ticker}')

    url = f'{YAHOO_FINANCE_BASE_URL}/{ticker.upper()}'
    params = {
        'range': '1y',
        'interval': '1d',
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }

    response = requests.get(url, params=params, headers=headers, timeout=15)
    response.raise_for_status()
    data = response.json()

    chart = data.get('chart', {})
    if chart.get('error'):
        error_msg = chart['error'].get('description', 'Unknown error')
        raise ValueError(f"Yahoo Finance error: {error_msg}")

    result_data = chart.get('result')
    if not result_data:
        raise ValueError(f"No data found for ticker: {ticker}")

    result_item = result_data[0]
    meta = result_item.get('meta', {})
    timestamps = result_item.get('timestamp', [])
    indicators = result_item.get('indicators', {})
    quotes = indicators.get('quote', [{}])[0]
    closes = quotes.get('close', [])
    opens = quotes.get('open', [])

    # Filter out None values and pair with timestamps
    valid_data = [
        (ts, c, o)
        for ts, c, o in zip(timestamps, closes, opens)
        if c is not None
    ]

    if not valid_data:
        raise ValueError(f"No valid price data for: {ticker}")

    # Current (most recent) price
    latest_ts, latest_close, latest_open = valid_data[-1]
    current_price = round(latest_close, 2)
    current_date = datetime.fromtimestamp(latest_ts).strftime('%Y-%m-%d')

    open_price = latest_open if latest_open else current_price
    daily_change, daily_change_percent = calculate_change(current_price, open_price)

    result = {
        'symbol': ticker.upper(),
        'price': current_price,
        'currency': meta.get('currency', 'USD'),
        'change': daily_change,
        'changePercent': daily_change_percent,
        'timestamp': current_date,
    }

    # Build date->price map
    date_price_map = {}
    for ts, close, _ in valid_data:
        date_str = datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
        date_price_map[date_str] = round(close, 2)

    all_dates = list(date_price_map.keys())

    # 5 trading days ago
    if len(valid_data) > 5:
        price_5 = round(valid_data[-6][1], 2)
        change_5, change_pct_5 = calculate_change(current_price, price_5)
        result['price5DaysAgo'] = price_5
        result['change5Days'] = change_5
        result['changePercent5Days'] = change_pct_5

    # 30 trading days ago
    if len(valid_data) > 30:
        price_30 = round(valid_data[-31][1], 2)
        change_30, change_pct_30 = calculate_change(current_price, price_30)
        result['price30DaysAgo'] = price_30
        result['change30Days'] = change_30
        result['changePercent30Days'] = change_pct_30

    # Fixed dates
    april_date = find_closest_date(all_dates, FIXED_DATES['april1_2025'])
    if april_date:
        price_april = date_price_map[april_date]
        change_a, change_pct_a = calculate_change(current_price, price_april)
        result['priceApril1_2025'] = price_april
        result['changeApril1'] = change_a
        result['changePercentApril1'] = change_pct_a

    october_date = find_closest_date(all_dates, FIXED_DATES['october1_2025'])
    if october_date:
        price_october = date_price_map[october_date]
        change_o, change_pct_o = calculate_change(current_price, price_october)
        result['priceOctober1_2025'] = price_october
        result['changeOctober1'] = change_o
        result['changePercentOctober1'] = change_pct_o

    december_date = find_closest_date(all_dates, FIXED_DATES['december1_2025'])
    if december_date:
        price_december = date_price_map[december_date]
        change_d, change_pct_d = calculate_change(current_price, price_december)
        result['priceDecember1_2025'] = price_december
        result['changeDecember1'] = change_d
        result['changePercentDecember1'] = change_pct_d

    print(f'✅ Yahoo Finance: {ticker} = ${current_price}')
    return result


# ─── Flask Routes ────────────────────────────────────────────────────────────

@app.route('/')
def index():
    """Render main application page."""
    return render_template('index.html')


@app.route('/api/alpha-vantage/<ticker>')
def get_alpha_vantage(ticker: str):
    """Fetch stock data from Alpha Vantage."""
    if not ALPHA_VANTAGE_API_KEY:
        return jsonify({'error': 'Alpha Vantage API key not configured. Please add it to your .env file.'}), 500
    try:
        data = fetch_alpha_vantage(ticker)
        return jsonify(data)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Request timed out. Please try again.'}), 504
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Network error: {str(e)}'}), 502
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500


@app.route('/api/yahoo-finance/<ticker>')
def get_yahoo_finance(ticker: str):
    """Fetch stock data from Yahoo Finance (bypasses CORS via server-side request)."""
    try:
        data = fetch_yahoo_finance(ticker)
        return jsonify(data)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return jsonify({'error': f'Ticker "{ticker}" not found on Yahoo Finance.'}), 404
        return jsonify({'error': f'HTTP error: {str(e)}'}), 502
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Request timed out. Please try again.'}), 504
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Network error: {str(e)}'}), 502
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok', 'message': 'Stock Price Check App is running'})


if __name__ == '__main__':
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    print(f'🚀 Starting Stock Price Check App on http://localhost:{port}')
    print(f'   Alpha Vantage API Key: {"✅ configured" if ALPHA_VANTAGE_API_KEY else "❌ not set"}')
    app.run(host=host, port=port, debug=debug)
