"""
Stock Price Check App - Flask Backend
======================================
Routes only. All data-fetching logic lives in the providers/ package.

To add a new data source:
  - Create providers/<name>.py with a fetch(ticker) function
  - Register it in providers/__init__.py
  - No changes needed here
"""

import os
import requests
from flask import Flask, render_template, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from providers import get_provider, REGISTRY

load_dotenv()

app = Flask(__name__)
CORS(app)


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    """Render main application page."""
    return render_template('index.html')


@app.route('/api/<provider>/<ticker>')
def get_stock_data(provider: str, ticker: str):
    """
    Unified stock data endpoint. Delegates to the registered provider.

    URL examples:
      GET /api/alpha-vantage/AAPL
      GET /api/yahoo-finance/AAPL
    """
    fetch = get_provider(provider)
    if fetch is None:
        available = list(REGISTRY.keys())
        return jsonify({
            'error': f'Unknown provider "{provider}". Available: {available}'
        }), 400

    try:
        data = fetch(ticker)
        return jsonify(data)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except requests.exceptions.HTTPError as e:
        if hasattr(e, 'response') and e.response is not None and e.response.status_code == 404:
            return jsonify({'error': f'Ticker "{ticker}" not found.'}), 404
        return jsonify({'error': f'HTTP error: {str(e)}'}), 502
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Request timed out. Please try again.'}), 504
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Network error: {str(e)}'}), 502
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500


@app.route('/health')
def health():
    """Health check — also reports which providers are registered."""
    return jsonify({
        'status': 'ok',
        'providers': list(REGISTRY.keys()),
    })


# ─── Entry point ──────────────────────────────────────────────────────────────

if __name__ == '__main__':
    host  = os.environ.get('HOST', '0.0.0.0')
    port  = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    alpha_key = os.environ.get('ALPHA_VANTAGE_API_KEY', '')
    print(f'🚀 Starting Stock Price Check App on http://localhost:{port}')
    print(f'   Alpha Vantage API Key : {"✅ configured" if alpha_key else "❌ not set"}')
    print(f'   Registered providers  : {list(REGISTRY.keys())}')
    app.run(host=host, port=port, debug=debug)
