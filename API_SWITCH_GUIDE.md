# API Switch Guide

## Overview

The Stock Price Checker supports two data sources. A toggle switch in the UI lets you switch between them without reloading the page.

## Toggle Switch Location

The toggle is positioned between the title and the input field:

```
📈 Stock Price Checker
Enter a stock ticker to get the current price

Data Source:  [Alpha Vantage] ●——○ [Yahoo Finance]

[ Enter stock ticker (e.g., AAPL, MSFT, GOOGL) ] [Price]
```

## How the Toggle Works

| Position | Color | API Used |
|----------|-------|----------|
| Left (OFF) | Blue (#667eea) | Alpha Vantage |
| Right (ON) | Green (#10b981) | Yahoo Finance |

1. Default position is **left = Alpha Vantage**
2. Clicking/tapping the switch slides it to the right
3. The label highlights the active API name
4. Switching clears previous results automatically

## API Comparison

| Feature | Alpha Vantage | Yahoo Finance |
|---------|---------------|---------------|
| Setup required | Yes (free API key) | No |
| Free tier limit | 25 calls/day | Unlimited (unofficial) |
| Rate limit | 5 calls/minute | None known |
| Data quality | High (official) | Good (unofficial) |
| Reliability | Official | Unofficial (may change) |
| Historical depth | 20+ years | ~1 year range |
| CORS | Works directly | Requires backend proxy |

## When to Use Each API

### Use Alpha Vantage when:
- You have a valid API key set up
- You need official, reliable data
- You are doing fewer than 25 lookups per day
- You need data from many years ago

### Use Yahoo Finance when:
- You do not have an Alpha Vantage key yet
- You have hit the Alpha Vantage rate limit
- You need quick, unlimited lookups
- The most recent year of data is sufficient

## Backend Routes

Each API has its own Flask route:

```
GET /api/alpha-vantage/<ticker>   → Alpha Vantage handler
GET /api/yahoo-finance/<ticker>   → Yahoo Finance handler
```

The JavaScript fetch URL is chosen based on the toggle state:

```javascript
const api = document.getElementById('apiToggle').checked
    ? 'yahoo-finance'
    : 'alpha-vantage';

const response = await fetch(`/api/${api}/${ticker}`);
```

## Testing Both APIs

1. Start Flask: `python app.py`
2. Open http://localhost:5000
3. Toggle LEFT → enter AAPL → click Price (Alpha Vantage)
4. Toggle RIGHT → enter AAPL → click Price (Yahoo Finance)
5. Compare the results (prices should be very close)

## Error Scenarios

| Error | Cause | Solution |
|-------|-------|----------|
| "API key not configured" | .env missing | Create .env file with key |
| "Rate limit reached" | 25/day exceeded | Switch to Yahoo Finance |
| "Ticker not found" | Invalid symbol | Check the ticker spelling |
| Network error | Flask not running | Run `python app.py` |
