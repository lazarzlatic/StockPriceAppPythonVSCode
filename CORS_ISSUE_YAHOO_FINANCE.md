# CORS Issue with Yahoo Finance

## What is CORS?

CORS (Cross-Origin Resource Sharing) is a browser security mechanism that blocks web pages from making requests to a different domain than the one that served the page.

**Example of a CORS-blocked request:**

```
Your page: http://localhost:5000
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
'http://localhost:5000' has been blocked by CORS policy: No
'Access-Control-Allow-Origin' header is present on the requested resource.
```

Yahoo Finance does not include the `Access-Control-Allow-Origin` header in its responses, so browsers refuse to expose the data to JavaScript.

## The Solution: Flask Backend Proxy

A Flask route makes the request **server-side**, where CORS rules do not apply:

```
Browser (blocked by CORS if direct)
    ↓
Flask route /api/yahoo-finance/<ticker>   ← Same origin as the page
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

```python
@app.route('/api/yahoo-finance/<ticker>')
def get_yahoo_finance(ticker: str):
    url = f'https://query2.finance.yahoo.com/v8/finance/chart/{ticker}'
    headers = {'User-Agent': 'Mozilla/5.0 ...'}
    response = requests.get(url, headers=headers)  # Server-side, no CORS
    data = response.json()
    # Parse and return
    return jsonify(parsed_data)
```

The JavaScript calls the Flask route (same origin):

```javascript
// This WORKS - calling our own Flask server
const response = await fetch('/api/yahoo-finance/AAPL');
```

## Flask-CORS

The app also uses `flask-cors` to allow the browser to call Flask routes from different origins (if needed in future):

```python
from flask_cors import CORS
CORS(app)
```

This adds the `Access-Control-Allow-Origin: *` header to Flask responses.

## Alternative Solutions

| Solution | Pros | Cons |
|----------|------|------|
| Flask proxy (our approach) | Works, no API key needed | Must keep Flask running |
| Alpha Vantage | Official API, CORS-friendly | 25 calls/day limit |
| CORS proxy services | Easy to set up | Third-party, not reliable |
| Browser extension | Works locally | Requires extension installed |

## Summary

- Yahoo Finance blocks browser JavaScript requests via CORS
- Our Flask backend makes the request server-side (CORS does not apply)
- The browser calls `/api/yahoo-finance/<ticker>` on our own Flask server
- Flask forwards the request to Yahoo Finance and returns the data
- This is a common and valid pattern called a **backend proxy**
