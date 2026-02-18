# CORS Issue with Yahoo Finance

## What is CORS?

CORS (Cross-Origin Resource Sharing) is a browser security mechanism that blocks web pages from making requests to a different domain than the one that served the page.

**Example of a CORS-blocked request:**

```
Your page: http://localhost:8080
Yahoo Finance: https://query2.finance.yahoo.com

→ Browser blocks this because the domains are different!
```

## Why Yahoo Finance Cannot Be Called Directly

If JavaScript tries to fetch from Yahoo Finance directly:

```javascript
// This FAILS in the browser (CORS error)
const response = await fetch('https://query2.finance.yahoo.com/v8/finance/chart/AAPL');
```

The browser will show an error like:

```
Access to fetch at 'https://query2.finance.yahoo.com/...' from origin
'http://localhost:8080' has been blocked by CORS policy: No
'Access-Control-Allow-Origin' header is present on the requested resource.
```

Yahoo Finance does not include the `Access-Control-Allow-Origin` header in its responses, so browsers refuse to expose the data to JavaScript.

## Which Providers Have CORS Issues

| Provider | CORS Issue? | Reason |
|----------|------------|--------|
| Alpha Vantage | No | Includes CORS headers |
| Yahoo Finance | **Yes** | No CORS headers (unofficial API) |
| FMP | No | Includes CORS headers |
| Massive | No | Includes CORS headers |

All providers are called via Flask backend anyway, so CORS is never an issue in practice.

## The Solution: Flask Backend Proxy

A Flask route makes the request **server-side**, where CORS rules do not apply:

```
Browser (blocked by CORS if direct)
    ↓
Flask route /api/<provider>/<ticker>   ← Same origin as the page
    ↓
requests.get('https://query2.finance.yahoo.com/...')  ← No CORS, server-to-server
    ↓
Returns JSON to browser
```

### Why it works:

| Context | CORS Applies? |
|---------|--------------|
| Browser JavaScript | YES - CORS is enforced |
| Python requests (server) | NO - CORS is a browser policy only |
| curl / Postman | NO - CORS is browser-only |

## Flask Implementation

All providers go through the same unified route:

```python
@app.route('/api/<provider>/<ticker>')
def get_stock_data(provider: str, ticker: str):
    fetch = get_provider(provider)
    data = fetch(ticker)          # server-side request, no CORS
    return jsonify(data)
```

The JavaScript always calls our own Flask server:

```javascript
// This WORKS - calling our own Flask server (same origin)
const response = await fetch('/api/yahoo-finance/AAPL');
const response = await fetch('/api/fmp/AAPL');
```

## Flask-CORS

The app also uses `flask-cors` to allow the browser to call Flask routes from different origins (useful if the frontend is ever served separately):

```python
from flask_cors import CORS
CORS(app)
```

This adds the `Access-Control-Allow-Origin: *` header to all Flask responses.

## Alternative Solutions

| Solution | Pros | Cons |
|----------|------|------|
| Flask proxy (our approach) | Works for all providers | Must keep Flask running |
| Alpha Vantage | Official API, CORS-friendly | 25 calls/day limit |
| FMP | Official API, CORS-friendly | Requires free key |
| Massive | Official API, CORS-friendly | Requires free key |
| CORS proxy services | Easy to set up | Third-party, not reliable |

## Summary

- Yahoo Finance blocks browser JavaScript requests via CORS
- All 4 providers are called via our Flask backend (server-side, no CORS)
- The browser always calls `/api/<provider>/<ticker>` on our own Flask server
- Flask forwards the request to the provider and returns the data
- This is a common and valid pattern called a **backend proxy**
