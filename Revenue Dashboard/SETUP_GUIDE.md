# Python and Dashboard Setup Guide

## Step 1: Check if Python is Installed

Double-click `check_python.bat` on your Desktop.

### If you see Python version numbers:
Great! Python is installed. Skip to **Step 3**.

### If you see an error or "command not found":
Python is not installed or not in PATH. Continue to **Step 2**.

---

## Step 2: Install Python

### Option A: Download and Install Python (Recommended)

1. Go to https://www.python.org/downloads/
2. Click "Download Python 3.12.x" (or latest version)
3. **IMPORTANT**: When installing, CHECK the box that says **"Add Python to PATH"**
4. Click "Install Now"
5. Wait for installation to complete
6. Restart PowerShell/Command Prompt
7. Run `check_python.bat` again to verify

### Option B: Install via Microsoft Store

1. Open Microsoft Store
2. Search for "Python 3.12"
3. Click "Get" or "Install"
4. After installation, restart PowerShell
5. Run `check_python.bat` to verify

---

## Step 3: Install Dashboard Packages

After confirming Python is installed, open PowerShell or Command Prompt and run:

### Method 1: Using pip (try this first)
```powershell
cd C:\Users\rwilcox\Desktop
pip install -r requirements.txt
```

### Method 2: Using python -m pip (if Method 1 doesn't work)
```powershell
cd C:\Users\rwilcox\Desktop
python -m pip install -r requirements.txt
```

### Method 3: Using py command (Windows alternative)
```powershell
cd C:\Users\rwilcox\Desktop
py -m pip install -r requirements.txt
```

### Method 4: Install packages one by one
```powershell
python -m pip install streamlit
python -m pip install pandas
python -m pip install plotly
python -m pip install openpyxl
```

---

## Step 4: Run the Dashboard

After packages are installed, run ONE of these commands:

### Option A: Double-click the batch file
Just double-click `run_dashboard.bat` on your Desktop

### Option B: Run from PowerShell
```powershell
cd C:\Users\rwilcox\Desktop
streamlit run revenue_dashboard.py
```

### Option C: Run using python command
```powershell
cd C:\Users\rwilcox\Desktop
python -m streamlit run revenue_dashboard.py
```

The dashboard will automatically open in your default web browser!

---

## Troubleshooting

### "pip is not recognized"
- Python is not in your PATH
- Solution: Reinstall Python and CHECK "Add Python to PATH" during installation
- Or use `python -m pip` instead of `pip`

### "streamlit: command not found" when running dashboard
- Solution: Use `python -m streamlit run revenue_dashboard.py` instead

### "No module named streamlit"
- Packages aren't installed
- Solution: Run the install commands from Step 3

### Dashboard starts but shows "File not found" error
- Make sure `rev9.csv` is in the same folder as `revenue_dashboard.py` (both should be on Desktop)

### Permission errors during installation
- You may need administrator privileges
- Solution: Right-click PowerShell → "Run as Administrator" → Try installation again

---

## Quick Reference Commands

**Check Python version:**
```
python --version
```

**Check pip version:**
```
python -m pip --version
```

**Install a package:**
```
python -m pip install package_name
```

**Run the dashboard:**
```
streamlit run revenue_dashboard.py
```
or
```
python -m streamlit run revenue_dashboard.py
```

---

## Need More Help?

If you're still having issues:
1. Send me the exact error message you're seeing
2. Tell me the output of `check_python.bat`
3. Let me know which Windows version you're using
