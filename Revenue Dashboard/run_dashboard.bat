@echo off
echo Starting Revenue Collections Dashboard...
echo.
echo Make sure you have installed the required packages first!
echo If not, run: python -m pip install -r requirements.txt
echo.
cd /d "%~dp0"
python -m streamlit run revenue_dashboard.py
pause
