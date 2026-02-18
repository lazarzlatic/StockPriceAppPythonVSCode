# Yahoo Finance Setup Guide

## No API Key Required

Yahoo Finance does not require an API key. However, it cannot be called directly from the browser due to CORS restrictions (see CORS_ISSUE_YAHOO_FINANCE.md).

## How It Works

The Flask backend acts as a proxy:

```
Browser (JavaScript)
    → POST /api/yahoo-finance/AAPL   (same-origin, no CORS issue)
        → Flask backend
            → Yahoo Finance API      (server-side, no CORS)
        ← Returns JSON
    ← Displays results
```

## Flask Backend Route

```python
@app.route('/api/yahoo-finance/<ticker>')
def get_yahoo_finance(ticker: str):
    url = f'https://query2.finance.yahoo.com/v8/finance/chart/{ticker}'
    params = {'range': '1y', 'interval': '1d'}
    headers = {'User-Agent': 'Mozilla/5.0 ...'}
    response = requests.get(url, params=params, headers=headers)
    # Parse and return structured JSON
```

## Yahoo Finance API Details

- **Endpoint**: `https://query2.finance.yahoo.com/v8/finance/chart/<SYMBOL>`
- **Parameters**: `range=1y` (1 year of data), `interval=1d` (daily)
- **Method**: GET
- **Authentication**: None required
- **Rate Limits**: None officially published (unofficial API)

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
🚀 Starting Stock Price Check App on http://localhost:5000
   Alpha Vantage API Key: ✅ configured   (or ❌ not set)
```

### 2. Open the app

Navigate to: http://localhost:5000

### 3. Select Yahoo Finance

Toggle the switch to the **right** (green position).

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
      "meta": { "currency": "USD", "symbol": "AAPL" },
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

## Common Issues

**Port already in use:**
```bash
# Find process using port 5000
netstat -ano | findstr :5000      # Windows
lsof -i :5000                     # macOS/Linux

# Kill the process or use a different port
PORT=5001 python app.py
```

**Yahoo Finance blocked:**
- This uses an unofficial endpoint that may change
- Try again after a few minutes
- Switch to Alpha Vantage as a fallback
