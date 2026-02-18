# Yahoo Finance Setup Guide

## No API Key Required

Yahoo Finance is the only provider that requires **no API key**. It works out of the box.
However, it cannot be called directly from the browser due to CORS restrictions
(see CORS_ISSUE_YAHOO_FINANCE.md). All providers are accessed through the Flask backend.

## How It Works

The Flask backend acts as a proxy:

```
Browser (JavaScript)
    → GET /api/yahoo-finance/AAPL   (same-origin, no CORS issue)
        → Flask backend
            → Yahoo Finance API      (server-side, no CORS)
        ← Returns JSON
    ← Displays results
```

## Flask Backend Route (Unified)

All providers share a single route in `app.py`:

```python
@app.route('/api/<provider>/<ticker>')
def get_stock_data(provider: str, ticker: str):
    fetch = get_provider(provider)   # looks up 'yahoo-finance' in REGISTRY
    data = fetch(ticker)             # calls providers/yahoo_finance.py fetch()
    return jsonify(data)
```

The Yahoo Finance fetch logic lives in `providers/yahoo_finance.py`:

```python
def fetch(ticker: str) -> dict:
    url = f'https://query2.finance.yahoo.com/v8/finance/chart/{ticker}'
    params = {'range': '1y', 'interval': '1d'}
    headers = {'User-Agent': 'Mozilla/5.0 ...'}
    response = requests.get(url, params=params, headers=headers)
    # Parse and return structured dict
```

## Yahoo Finance API Details

- **Endpoint**: `https://query2.finance.yahoo.com/v8/finance/chart/<SYMBOL>`
- **Parameters**: `range=1y` (1 year of data), `interval=1d` (daily)
- **Method**: GET
- **Authentication**: None required
- **Rate Limits**: None officially published (unofficial API)
- **Company Name**: extracted from `meta.longName` or `meta.shortName`

## Step-by-Step Usage

### 1. Start Flask

```bash
# Activate virtual environment first
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux

# Start the server
python app.py
```

You should see:
```
🚀 Starting Stock Price Check App on http://localhost:8080
   Alpha Vantage API Key : ✅ configured   (or ❌ not set)
   Registered providers  : ['alpha-vantage', 'yahoo-finance', 'fmp', 'massive']
```

### 2. Open the app

Navigate to: **http://localhost:8080**

### 3. Select Yahoo Finance

Click the **Yahoo Finance** pill in the selector.

### 4. Enter a ticker

Type `AAPL` (or any valid ticker) and press **Price**.

### 5. View results

The backend logs will show:
```
📊 Yahoo Finance: fetching AAPL
✅ Yahoo Finance: AAPL = $220.50
```

## Response Data Structure

Yahoo Finance returns timestamps (Unix epoch) and price arrays:

```json
{
  "chart": {
    "result": [{
      "meta": { "currency": "USD", "symbol": "AAPL", "longName": "Apple Inc." },
      "timestamp": [1704067200, 1704153600, ...],
      "indicators": {
        "quote": [{
          "open":  [185.0, 186.2, ...],
          "close": [185.9, 187.1, ...]
        }]
      }
    }]
  }
}
```

The backend converts timestamps to `YYYY-MM-DD` strings and maps them to prices.
Company name is extracted from `meta.longName` or `meta.shortName`.

## Common Issues

**Port already in use:**
```bash
# Find process using port 8080
netstat -ano | findstr :8080      # Windows
lsof -i :8080                     # macOS/Linux

# Or use a different port
PORT=9000 python app.py
```

**Yahoo Finance blocked:**
- This uses an unofficial endpoint that may change
- Try again after a few minutes
- Switch to FMP or Alpha Vantage as a fallback
