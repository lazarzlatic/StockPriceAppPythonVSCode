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
git clone <your-repo-url>
cd StockPriceCheckApp
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

### Step 5: Configure Alpha Vantage API Key

1. Get a free key at: https://www.alphavantage.co/support/#api-key
   (registration is free, takes ~1 minute)

2. Create your `.env` file:
   ```bash
   # Windows
   copy .env.example .env

   # macOS/Linux
   cp .env.example .env
   ```

3. Open `.env` and add your key:
   ```
   ALPHA_VANTAGE_API_KEY=your_actual_key_here
   SECRET_KEY=any-random-string-here
   FLASK_ENV=development
   ```

**Note:** Yahoo Finance works without any API key.

### Step 6: Run the Application

```bash
python app.py
```

Expected output:
```
🚀 Starting Stock Price Check App on http://localhost:5000
   Alpha Vantage API Key: ✅ configured
 * Running on http://0.0.0.0:5000
 * Debug mode: on
```

### Step 7: Open the App

Open your browser and go to: **http://localhost:5000**

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

**Port 5000 already in use:**
```bash
# Change the port
PORT=5001 python app.py
# Then open http://localhost:5001
```

**Permission denied (Windows):**
- Run Command Prompt as Administrator
- Or use: `python -m flask run`
