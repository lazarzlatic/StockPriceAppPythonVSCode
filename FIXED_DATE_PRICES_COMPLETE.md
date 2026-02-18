# Fixed Date Prices - Technical Guide

## Overview

The app shows stock prices for three specific historical dates:

| Date | Label |
|------|-------|
| April 1st, 2025 | Early 2025 snapshot |
| October 1st, 2025 | Mid-2025 snapshot |
| December 1st, 2025 | Late-2025 snapshot |

## Why 1 Year of Data is Required

All providers are configured to fetch **at least 1 full year** of daily data:

| Provider | Data Range | Configuration |
|----------|-----------|---------------|
| Alpha Vantage | 20+ years | `outputsize=full` |
| Yahoo Finance | ~1 year | `range=1y&interval=1d` |
| FMP | Flexible | `from=<400-days-ago>` |
| Massive | ~1 year | date range from 400 days ago to today |

If only 3 months of data were requested, April 1st and October 1st 2025 would not be available. Fetching ~1 year ensures all three dates are covered.

## How Closest Trading Day is Found

Stock markets are closed on weekends and holidays. The target dates (April 1, October 1, December 1) may not have price data if they fall on non-trading days.

The `find_closest_date()` function in `providers/base.py` searches outward from the target date:

```python
def find_closest_date(dates: list, target_date: str) -> str | None:
    target = datetime.strptime(target_date, '%Y-%m-%d')
    for delta in range(8):
        for direction in [1, -1]:
            candidate = target + timedelta(days=delta * direction)
            candidate_str = candidate.strftime('%Y-%m-%d')
            if candidate_str in dates:
                return candidate_str
    return None
```

**Search pattern for April 1, 2025:**
```
Day 0: 2025-04-01 → check
Day +1: 2025-04-02 → check
Day -1: 2025-03-31 → check
Day +2: 2025-04-03 → check
Day -2: 2025-03-30 → check
...up to ±7 days
```

The first date found in the data is used. Returns `None` if no trading day found within 7 days (extremely rare).

## Shared Fixed Dates (providers/base.py)

All providers use the same constants:

```python
FIXED_DATES = {
    'april1_2025':    '2025-04-01',
    'october1_2025':  '2025-10-01',
    'december1_2025': '2025-12-01',
}
```

## Alpha Vantage Implementation

Alpha Vantage returns data as a dictionary keyed by date string:

```python
time_series = {
    '2025-04-01': {'1. open': '..', '4. close': '170.23', ...},
    '2025-03-31': {'4. close': '169.85', ...},
    ...
}

all_dates = list(time_series.keys())  # ['2025-04-01', '2025-03-31', ...]

april_date = find_closest_date(all_dates, '2025-04-01')
if april_date:
    price = float(time_series[april_date]['4. close'])
```

## Yahoo Finance Implementation

Yahoo Finance returns parallel arrays of timestamps and prices:

```python
timestamps = [1743465600, 1743552000, ...]   # Unix epoch seconds
closes     = [170.23, 169.85, ...]

# Convert to date->price map
date_price_map = {}
for ts, close in zip(timestamps, closes):
    if close is not None:
        date_str = datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
        date_price_map[date_str] = round(close, 2)

all_dates = list(date_price_map.keys())
april_date = find_closest_date(all_dates, '2025-04-01')
```

## FMP Implementation

FMP returns an array of objects with date and close fields:

```python
# Response can be a flat array or {"historical": [...]}
records = data if isinstance(data, list) else data.get('historical', [])

# Records are newest-first: [{"date": "2025-04-01", "close": 170.23}, ...]
date_price_map = {r['date']: r['close'] for r in records if r.get('close') is not None}

all_dates = list(date_price_map.keys())
april_date = find_closest_date(all_dates, '2025-04-01')
```

## Massive Implementation

Massive returns aggregates (OHLCV bars) sorted descending:

```python
# results = [{"t": 1743465600000, "c": 170.23, ...}, ...]  (milliseconds)
date_price_map = {}
for bar in results:
    ts_ms = bar['t']
    date_str = datetime.fromtimestamp(ts_ms / 1000).strftime('%Y-%m-%d')
    date_price_map[date_str] = round(bar['c'], 2)

all_dates = list(date_price_map.keys())
april_date = find_closest_date(all_dates, '2025-04-01')
```

## Change Calculation

Once the price for the fixed date is found, the change to current is calculated using `calculate_change()` in `providers/base.py`:

```python
def calculate_change(current: float, previous: float) -> tuple:
    change = current - previous
    percent_change = (change / previous * 100) if previous != 0 else 0
    return round(change, 2), round(percent_change, 2)

change, pct = calculate_change(current_price, price_april)
# e.g., change = +12.50, pct = +7.35
```

## UI Display

Each date card shows:
- **Date label**: "April 1st, 2025"
- **Price**: $XXX.XX (price on that date)
- **Change**: 🟢 +$12.50 (+7.35%) or 🔴 -$8.20 (-4.61%)

If no data is found for a date: "—" / "No data" is shown.

## Grid Layout

The three date cards use CSS Grid with 3 columns:

```css
.fixed-dates-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
}

/* Mobile: single column */
@media (max-width: 420px) {
    .fixed-dates-grid {
        grid-template-columns: 1fr;
    }
}
```

## Testing Fixed Dates

To verify the fixed dates work:

1. Run `python app.py`
2. Open http://localhost:8080
3. Select any provider pill
4. Search for AAPL
5. Scroll down to see the 3 date cards
6. All three should show a price

If a date shows "No data", the market may have been closed for an extended period around that date, which is extremely unlikely for major US stocks.
