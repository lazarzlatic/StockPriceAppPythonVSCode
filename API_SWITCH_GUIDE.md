# API Provider Selector Guide

## Overview

The Stock Price Checker supports **4 data providers**. A pill button group in the UI lets you switch between them without reloading the page.

## Pill Selector Location

The selector is positioned between the title and the input field:

```
📈 Stock Price Checker
Enter a stock ticker to get the current price

              Data Source:
[ Alpha Vantage ]  [ Yahoo Finance ]  [ FMP ]  [ Massive ]

[ Enter stock ticker (e.g., AAPL, MSFT, GOOGL) ] [Price]
```

## How the Pill Selector Works

- The active pill has a **gradient background** (blue → purple)
- Clicking any pill activates it and clears previous results
- Default selection is **Alpha Vantage**

## Provider Comparison

| Feature | Alpha Vantage | Yahoo Finance | FMP | Massive |
|---------|--------------|---------------|-----|---------|
| API key required | Yes | No | Yes | Yes |
| Free tier limit | 25 req/day | Unlimited | 250 req/day | Free tier |
| Rate limit | 5 req/min | None | None known | None known |
| Data quality | High (official) | Good (unofficial) | High (official) | High (official) |
| Historical depth | 20+ years | ~1 year | Flexible | ~1 year |
| Company name source | OVERVIEW endpoint | meta.longName | quote.name | reference/tickers |
| CORS restriction | No | Yes (backend proxy) | No | No |
| Extra API calls | 1 (OVERVIEW for name) | 0 | 0 | 1 (reference for name) |

## When to Use Each Provider

### Alpha Vantage
- You need 20+ years of historical data
- You need official, reliable data quality
- You are doing fewer than 25 lookups per day

### Yahoo Finance
- You do not have any API key set up yet
- You have hit another provider's rate limit
- You need quick, unlimited lookups
- 1 year of historical data is sufficient

### FMP (Financial Modeling Prep)
- You need up to 250 lookups per day
- You want an official, stable API
- Get a free key at: https://financialmodelingprep.com/register

### Massive
- You want a Polygon.io-compatible API
- You have a Massive API key
- Get a free key at: https://massive.com

## Backend Routes

All providers use the **single unified route** in `app.py`:

```
GET /api/<provider>/<ticker>
```

Examples:
```
GET /api/alpha-vantage/AAPL
GET /api/yahoo-finance/AAPL
GET /api/fmp/AAPL
GET /api/massive/AAPL
```

The provider is resolved by the registry in `providers/__init__.py`:

```python
REGISTRY = {
    'alpha-vantage': _fetch_alpha_vantage,
    'yahoo-finance': _fetch_yahoo_finance,
    'fmp':           _fetch_fmp,
    'massive':       _fetch_massive,
}
```

## JavaScript — How Provider is Selected

```javascript
function getSelectedApi() {
    const active = document.querySelector('.api-pill.active');
    return active ? active.dataset.provider : 'yahoo-finance';
}

// Fetches from /api/alpha-vantage/AAPL, /api/fmp/AAPL, etc.
const response = await fetch(`/api/${getSelectedApi()}/${ticker}`);
```

## Testing All Providers

1. Start Flask: `python app.py`
2. Open http://localhost:8080
3. Click **Yahoo Finance** → enter AAPL → click Price (no key needed)
4. Click **Alpha Vantage** → enter AAPL → click Price (requires key)
5. Click **FMP** → enter AAPL → click Price (requires key)
6. Click **Massive** → enter AAPL → click Price (requires key)
7. Compare results — prices should be very close across all providers

## Error Scenarios

| Error | Cause | Solution |
|-------|-------|----------|
| "API key not configured" | .env missing key | Add key to .env file |
| "Rate limit reached" | 25/day (Alpha Vantage) | Switch to Yahoo Finance or FMP |
| "Ticker not found" | Invalid symbol | Check the ticker spelling |
| Network error | Flask not running | Run `python app.py` |
| 403 Forbidden | Provider plan restriction | Check API plan or try another provider |

## Adding a New Provider

1. Create `providers/<name>.py` with `fetch(ticker: str) -> dict`
2. Add one entry to `REGISTRY` in `providers/__init__.py`
3. Add one pill button in `templates/index.html`
4. `app.py` requires **zero changes**
