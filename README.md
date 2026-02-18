# 📈 Stock Price Checker

A professional Python/Flask web application for checking real-time stock prices with dual API support, beautiful UI, and historical price comparisons.

## Features

- **Dual API Support** - Switch between Alpha Vantage and Yahoo Finance
- **Current Price** - Real-time price with daily change
- **Historical Comparisons** - 5-day and 30-day price comparisons
- **Fixed Date Prices** - April 1st, October 1st, December 1st 2025
- **Toggle Switch** - Seamlessly switch data sources
- **Visual Indicators** - 🟢 green / 🔴 red for gains/losses
- **Responsive Design** - Works on desktop and mobile
- **Secure** - API key protected via .env file

## Technologies

- **Python 3.9+** - Backend language
- **Flask 3.0** - Web framework
- **Jinja2** - HTML templating
- **Requests** - HTTP API calls
- **Vanilla JavaScript** - Frontend interactivity
- **HTML5/CSS3** - UI and styling

## Installation

### 1. Prerequisites

- Python 3.9 or higher: https://www.python.org/downloads/

### 2. Clone or download the project

```bash
git clone <your-repo-url>
cd StockPriceCheckApp
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

### 5. Configure API key

Get a free Alpha Vantage key at: https://www.alphavantage.co/support/#api-key

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your key
ALPHA_VANTAGE_API_KEY=your_actual_key_here
```

### 6. Start the Flask server

```bash
python app.py
```

Or using Flask CLI:

```bash
flask run
```

### 7. Open the app

Visit http://localhost:5000 in your browser.

## How to Use

1. Select your data source using the toggle switch:
   - **Left (blue)** = Alpha Vantage
   - **Right (green)** = Yahoo Finance

2. Type a stock ticker in the input field

3. Press **Price** or hit **Enter**

4. View results:
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

## API Limits

| API | Free Tier Limit |
|-----|----------------|
| Alpha Vantage | 25 requests/day, 5/minute |
| Yahoo Finance | Unlimited (unofficial) |

## Troubleshooting

**"Alpha Vantage API key not configured"**
- Copy `.env.example` to `.env` and add your key

**"Rate limit reached"**
- Switch to Yahoo Finance using the toggle

**"Cannot connect to server"**
- Make sure Flask is running: `python app.py`
- Check that port 5000 is not in use

**Invalid ticker error**
- Double-check the ticker symbol is correct
- Try searching on https://finance.yahoo.com

## Project Structure

```
StockPriceCheckApp/
├── app.py              # Flask backend
├── requirements.txt    # Python dependencies
├── config.example.py   # Config template
├── .env.example        # Environment template
├── .gitignore
├── templates/
│   └── index.html      # Main HTML page
├── static/
│   ├── style.css       # Styles
│   └── script.js       # Frontend JS
└── *.md                # Documentation
```

## License

MIT License - Free to use and modify.
