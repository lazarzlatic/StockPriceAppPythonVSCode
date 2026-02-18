/**
 * Stock Price Checker - Frontend JavaScript
 * Handles UI interactions, API calls, and result display.
 */

// ─── State ────────────────────────────────────────────────────────────────────

let isLoading = false;

// ─── Helpers ──────────────────────────────────────────────────────────────────

/**
 * Format a dollar price value.
 * @param {number} price
 * @returns {string}
 */
function formatPrice(price) {
    if (price == null || isNaN(price)) return '—';
    return '$' + price.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

/**
 * Format a change value with indicator emoji and sign.
 * @param {number} change
 * @param {number} changePercent
 * @returns {{ html: string, cssClass: string }}
 */
function formatChange(change, changePercent) {
    if (change == null || isNaN(change)) return { html: '—', cssClass: '' };
    const isPositive = change >= 0;
    const sign = isPositive ? '+' : '';
    const indicator = isPositive ? '🟢' : '🔴';
    const cssClass = isPositive ? 'positive' : 'negative';
    const html = `${indicator} ${sign}${change.toFixed(2)} (${sign}${changePercent.toFixed(2)}%)`;
    return { html, cssClass };
}

/**
 * Hide all status/result panels.
 */
function hideMessages() {
    document.getElementById('loading').classList.add('hidden');
    document.getElementById('errorBox').classList.add('hidden');
    document.getElementById('results').classList.add('hidden');
}

/**
 * Show an error message to the user.
 * @param {string} message
 */
function showError(message) {
    hideMessages();
    const errorBox = document.getElementById('errorBox');
    document.getElementById('errorMessage').textContent = message;
    errorBox.classList.remove('hidden');
}

/**
 * Show loading indicator.
 */
function showLoading() {
    hideMessages();
    document.getElementById('loading').classList.remove('hidden');
}

/**
 * Get which API is currently selected.
 * @returns {'alpha-vantage' | 'yahoo-finance'}
 */
function getSelectedApi() {
    return document.getElementById('apiToggle').checked ? 'yahoo-finance' : 'alpha-vantage';
}

// ─── Display Result ───────────────────────────────────────────────────────────

/**
 * Populate the results panel with stock data.
 * @param {Object} data - Stock data returned from the backend
 */
function displayResult(data) {
    hideMessages();

    // Current Price
    document.getElementById('currentPrice').textContent = formatPrice(data.price);

    const dailyChangeEl = document.getElementById('dailyChange');
    if (data.change != null) {
        const { html, cssClass } = formatChange(data.change, data.changePercent);
        dailyChangeEl.innerHTML = html;
        dailyChangeEl.className = 'daily-change ' + cssClass;
    } else {
        dailyChangeEl.textContent = '';
    }

    // 5 Days Ago
    const price5El = document.getElementById('price5Days');
    const change5El = document.getElementById('change5Days');
    if (data.price5DaysAgo != null) {
        price5El.textContent = formatPrice(data.price5DaysAgo);
        const { html, cssClass } = formatChange(data.change5Days, data.changePercent5Days);
        change5El.innerHTML = html;
        change5El.className = 'hist-change ' + cssClass;
    } else {
        price5El.textContent = '—';
        change5El.textContent = 'N/A';
        change5El.className = 'hist-change';
    }

    // 30 Days Ago
    const price30El = document.getElementById('price30Days');
    const change30El = document.getElementById('change30Days');
    if (data.price30DaysAgo != null) {
        price30El.textContent = formatPrice(data.price30DaysAgo);
        const { html, cssClass } = formatChange(data.change30Days, data.changePercent30Days);
        change30El.innerHTML = html;
        change30El.className = 'hist-change ' + cssClass;
    } else {
        price30El.textContent = '—';
        change30El.textContent = 'N/A';
        change30El.className = 'hist-change';
    }

    // April 1st, 2025
    const priceAprilEl = document.getElementById('priceApril');
    const changeAprilEl = document.getElementById('changeApril');
    if (data.priceApril1_2025 != null) {
        priceAprilEl.textContent = formatPrice(data.priceApril1_2025);
        const { html, cssClass } = formatChange(data.changeApril1, data.changePercentApril1);
        changeAprilEl.innerHTML = html;
        changeAprilEl.className = 'date-change ' + cssClass;
    } else {
        priceAprilEl.textContent = '—';
        changeAprilEl.textContent = 'No data';
        changeAprilEl.className = 'date-change';
    }

    // October 1st, 2025
    const priceOctoberEl = document.getElementById('priceOctober');
    const changeOctoberEl = document.getElementById('changeOctober');
    if (data.priceOctober1_2025 != null) {
        priceOctoberEl.textContent = formatPrice(data.priceOctober1_2025);
        const { html, cssClass } = formatChange(data.changeOctober1, data.changePercentOctober1);
        changeOctoberEl.innerHTML = html;
        changeOctoberEl.className = 'date-change ' + cssClass;
    } else {
        priceOctoberEl.textContent = '—';
        changeOctoberEl.textContent = 'No data';
        changeOctoberEl.className = 'date-change';
    }

    // December 1st, 2025
    const priceDecemberEl = document.getElementById('priceDecember');
    const changeDecemberEl = document.getElementById('changeDecember');
    if (data.priceDecember1_2025 != null) {
        priceDecemberEl.textContent = formatPrice(data.priceDecember1_2025);
        const { html, cssClass } = formatChange(data.changeDecember1, data.changePercentDecember1);
        changeDecemberEl.innerHTML = html;
        changeDecemberEl.className = 'date-change ' + cssClass;
    } else {
        priceDecemberEl.textContent = '—';
        changeDecemberEl.textContent = 'No data';
        changeDecemberEl.className = 'date-change';
    }

    // Footer
    document.getElementById('currencyLabel').textContent = `Currency: ${data.currency || 'USD'}`;
    if (data.timestamp) {
        document.getElementById('lastUpdated').textContent = `Updated: ${data.timestamp}`;
    }

    document.getElementById('results').classList.remove('hidden');
}

// ─── Main Handler ─────────────────────────────────────────────────────────────

/**
 * Main handler for the Price button click (also called on Enter key).
 */
async function handlePriceClick() {
    if (isLoading) return;

    const input = document.getElementById('tickerInput');
    const ticker = input.value.trim().toUpperCase();

    if (!ticker) {
        showError('Please enter a stock ticker symbol (e.g., AAPL, MSFT, GOOGL).');
        input.focus();
        return;
    }

    if (!/^[A-Z0-9.^-]{1,10}$/.test(ticker)) {
        showError('Invalid ticker format. Please use letters and numbers only (e.g., AAPL, BRK.B).');
        return;
    }

    const api = getSelectedApi();
    const btn = document.getElementById('priceBtn');

    // Set loading state
    isLoading = true;
    btn.disabled = true;
    showLoading();

    try {
        const response = await fetch(`/api/${api}/${encodeURIComponent(ticker)}`);
        const data = await response.json();

        if (!response.ok) {
            showError(data.error || `Error fetching data for "${ticker}". Please check the ticker and try again.`);
            return;
        }

        if (data.error) {
            showError(data.error);
            return;
        }

        displayResult(data);
    } catch (err) {
        console.error('Fetch error:', err);
        if (err instanceof TypeError && err.message.includes('fetch')) {
            showError('Cannot connect to the server. Please make sure the Flask app is running on port 5000.');
        } else {
            showError(`Network error: ${err.message}. Please try again.`);
        }
    } finally {
        isLoading = false;
        btn.disabled = false;
    }
}

// ─── Event Listeners ──────────────────────────────────────────────────────────

// Enter key on input
document.getElementById('tickerInput').addEventListener('keydown', function (e) {
    if (e.key === 'Enter') {
        handlePriceClick();
    }
});

// Toggle switch - update active API label
document.getElementById('apiToggle').addEventListener('change', function () {
    const isYahoo = this.checked;
    const leftLabel = document.getElementById('apiNameLeft');
    const rightLabel = document.getElementById('apiNameRight');

    if (isYahoo) {
        leftLabel.classList.remove('active');
        rightLabel.classList.add('active');
    } else {
        leftLabel.classList.add('active');
        rightLabel.classList.remove('active');
    }

    // Clear previous results when switching API
    hideMessages();
});

// Focus input on page load and set initial active label
window.addEventListener('load', function () {
    document.getElementById('tickerInput').focus();
    document.getElementById('apiNameLeft').classList.add('active');
});
