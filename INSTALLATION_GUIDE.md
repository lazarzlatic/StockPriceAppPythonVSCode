# Installation Guide

## Prerequisites

### Python 3.9+

Download from: https://www.python.org/downloads/

**Verify installation:**
```bash
python --version
# Expected: Python 3.9.x or higher
```

### pip (included with Python)

```bash
pip --version
# Expected: pip 23.x.x or higher
```

## Step-by-Step Installation

### Step 1: Get the Project Files

Option A - Clone with git:
```bash
git clone https://github.com/lazarzlatic/StockPriceAppPythonVSCode.git
cd StockPriceAppPythonVSCode
```

Option B - Download ZIP and extract to a folder.

### Step 2: Create a Virtual Environment

A virtual environment isolates this project's dependencies from other Python projects.

**Windows:**
```bash
python -m venv venv
```

**macOS / Linux:**
```bash
python3 -m venv venv
```

You should see a new `venv/` folder created in the project.

### Step 3: Activate the Virtual Environment

**Windows (Command Prompt):**
```cmd
venv\Scripts\activate
```

**Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```

If PowerShell blocks the script, run first:
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

**macOS / Linux:**
```bash
source venv/bin/activate
```

After activation, your prompt will show `(venv)` at the start.

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- Flask 3.0.0 - Web framework
- flask-cors 4.0.0 - CORS support
- requests 2.31.0 - HTTP client
- python-dotenv 1.0.0 - .env file loader

**Verify installation:**
```bash
pip list
```

### Step 5: Configure API Keys

Copy the example file:
```bash
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

Open `.env` and add your keys:
```
ALPHA_VANTAGE_API_KEY=your_key   # https://www.alphavantage.co/support/#api-key
FMP_API_KEY=your_key             # https://financialmodelingprep.com/register
MASSIVE_API_KEY=your_key         # https://massive.com
SECRET_KEY=any-random-string
FLASK_ENV=development
```

**Notes:**
- **Yahoo Finance** requires no key — works out of the box
- **Alpha Vantage**: free key, 25 requests/day limit
- **FMP**: free key, 250 requests/day limit
- **Massive**: free key required

### Step 6: Run the Application

```bash
python app.py
```

Expected output:
```
🚀 Starting Stock Price Check App on http://localhost:8080
   Alpha Vantage API Key : ✅ configured   (or ❌ not set)
   FMP API Key           : ✅ configured   (or ❌ not set)
   Massive API Key       : ✅ configured   (or ❌ not set)
   Registered providers  : ['alpha-vantage', 'yahoo-finance', 'fmp', 'massive']
 * Running on http://0.0.0.0:8080
 * Debug mode: on
```

### Step 7: Open the App

Open your browser and go to: **http://localhost:8080**

## Deactivating the Virtual Environment

When you are done working:
```bash
deactivate
```

## Reinstalling Dependencies

If you need a clean install:
```bash
deactivate
rm -rf venv            # macOS/Linux
rmdir /s venv          # Windows

python -m venv venv
venv\Scripts\activate  # or source venv/bin/activate
pip install -r requirements.txt
```

## Troubleshooting

**"python not found":**
- Make sure Python is installed and added to PATH
- Try `python3` instead of `python`

**"pip not found":**
- Run: `python -m pip install --upgrade pip`

**"Module not found" error:**
- Make sure the virtual environment is activated (look for `(venv)` in prompt)
- Run `pip install -r requirements.txt` again

**Port 8080 already in use:**
```bash
# Find process using port 8080
netstat -ano | findstr :8080      # Windows
lsof -i :8080                     # macOS/Linux

# Or use a different port
PORT=9000 python app.py
# Then open http://localhost:9000
```

**"API key not configured" error:**
- Copy `.env.example` to `.env` and add the relevant key
- Yahoo Finance works without any key

**Permission denied (Windows):**
- Run Command Prompt as Administrator
- Or use: `python -m flask run`
