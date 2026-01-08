@echo off
echo Installing Required Packages for Revenue Dashboard...
echo.
echo This may take a few minutes...
echo.
cd /d "%~dp0"

echo Attempting installation method 1: python -m pip
python -m pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo Method 1 failed. Trying alternative method...
    echo.
    echo Installing packages individually...
    python -m pip install streamlit
    python -m pip install pandas
    python -m pip install plotly
    python -m pip install openpyxl
)

echo.
echo Installation complete!
echo.
echo You can now run the dashboard by double-clicking run_dashboard.bat
echo.
pause
