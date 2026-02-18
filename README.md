# 📈 Stock Price Checker

A professional Python/Flask web application for checking real-time stock prices with **4 data provider support**, beautiful UI, company name display, and comprehensive historical price comparisons.

## Features

- **4 Data Providers** - Alpha Vantage, Yahoo Finance, FMP, Massive
- **Provider Pill Selector** - Click any pill to switch data source instantly
- **Company Name Display** - Shows company name and ticker badge above price
- **Current Price** - Real-time price with daily change
- **Historical Comparisons** - 5-day and 30-day price comparisons
- **Fixed Date Prices** - April 1st, October 1st, December 1st 2025
- **Visual Indicators** - 🟢 green / 🔴 red for gains/losses
- **Responsive Design** - Works on desktop and mobile
- **Secure** - API keys protected via .env file
- **Extensible** - Add a 5th provider with 1 new file + 1 line of config

## Technologies

- **Python 3.9+** - Backend language
- **Flask 3.0** - Web framework
- **Jinja2** - HTML templating
- **Requests** - HTTP API calls
- **Vanilla JavaScript** - Frontend interactivity
- **HTML5/CSS3** - UI and styling

## Data Providers

| Provider | Key Required | Free Limit | Data Range | Notes |
|----------|-------------|------------|------------|-------|
| Alpha Vantage | Yes | 25 req/day, 5/min | 20+ years | Official, TIME_SERIES_DAILY |
| Yahoo Finance | No | Unlimited | ~1 year | Unofficial, no CORS |
| FMP | Yes | 250 req/day | Flexible | quote + historical light |
| Massive | Yes | Free tier | ~1 year | Polygon.io-compatible aggregates |

## Installation

### 1. Prerequisites

- Python 3.9 or higher: https://www.python.org/downloads/

### 2. Clone or download the project

```bash
git clone https://github.com/lazarzlatic/StockPriceAppPythonVSCode.git
cd StockPriceAppPythonVSCode
```

### 3. Create a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure API keys

```bash
# Copy the example file
cp .env.example .env
```

Edit `.env` and add your keys:
```
ALPHA_VANTAGE_API_KEY=your_key   # https://www.alphavantage.co/support/#api-key
FMP_API_KEY=your_key             # https://financialmodelingprep.com/register
MASSIVE_API_KEY=your_key         # https://massive.com
SECRET_KEY=any-random-string
FLASK_ENV=development
```

> **Yahoo Finance** requires no key — it works out of the box.

### 6. Start the Flask server

```bash
python app.py
```

### 7. Open the app

Visit **http://localhost:8080** in your browser.

## How to Use

1. Click a pill to select your data source:
   ```
   [ Alpha Vantage ]  [ Yahoo Finance ]  [ FMP ]  [ Massive ]
   ```

2. Type a stock ticker in the input field

3. Press **Price** or hit **Enter**

4. View results:
   - Company name and ticker badge
   - Current price with daily change
   - 5-day and 30-day historical comparisons
   - Fixed date prices (April, October, December 2025)

## Common Stock Tickers

| Ticker | Company |
|--------|---------|
| AAPL | Apple Inc. |
| MSFT | Microsoft Corporation |
| GOOGL | Alphabet Inc. (Google) |
| AMZN | Amazon.com Inc. |
| TSLA | Tesla Inc. |
| META | Meta Platforms Inc. |
| NVDA | NVIDIA Corporation |
| IBM | IBM Corporation |
| JPM | JPMorgan Chase & Co. |

## Troubleshooting

**"API key not configured"**
- Copy `.env.example` to `.env` and add the relevant key

**"Rate limit reached" (Alpha Vantage)**
- Switch to Yahoo Finance or FMP using the pills

**"Cannot connect to server"**
- Make sure Flask is running: `python app.py`
- App runs on port **8080**: http://localhost:8080

**Invalid ticker error**
- Double-check the ticker symbol is correct
- Try searching on https://finance.yahoo.com

## Project Structure

```
StockPriceAppPythonVSCode/
├── app.py              # Flask backend (routes only)
├── requirements.txt    # Python dependencies
├── config.example.py   # Config template
├── .env.example        # Environment template
├── .gitignore
├── providers/          # Data provider modules
│   ├── __init__.py     # Provider registry (REGISTRY + get_provider)
│   ├── base.py         # Shared helpers (find_closest_date, calculate_change)
│   ├── alpha_vantage.py
│   ├── yahoo_finance.py
│   ├── fmp.py
│   └── massive.py
├── templates/
│   └── index.html      # Main HTML page
├── static/
│   ├── style.css       # Styles
│   └── script.js       # Frontend JS
└── *.md                # Documentation
```

## Adding a 5th Provider

1. Create `providers/my_provider.py` with a `fetch(ticker: str) -> dict` function
2. Add one line to `providers/__init__.py`:
   ```python
   'my-provider': _fetch_my_provider,
   ```
3. Add a pill in `templates/index.html`:
   ```html
   <button class="api-pill" data-provider="my-provider">My Provider</button>
   ```
4. No changes to `app.py` needed

## License

MIT License - Free to use and modify.
