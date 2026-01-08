@echo off
echo ================================================================
echo Installing Packages for Forecast Comparison
echo ================================================================
echo.
echo Installing required packages:
echo   - scikit-learn (for Linear Trend forecasting)
echo   - numpy (for calculations)
echo.
echo This should take 1-2 minutes...
echo.
pause
echo.
cd /d "%~dp0"
echo Installing packages...
echo.
python -m pip install scikit-learn numpy
echo.
echo.
if %errorlevel% equ 0 (
    echo ================================================================
    echo Success! Required packages installed.
    echo ================================================================
    echo.
    echo You can now run: run_forecast_comparison.bat
    echo.
    echo Optional: To include Prophet (Bayesian) forecasting, also run:
    echo           install_prophet.bat
) else (
    echo ================================================================
    echo Installation failed.
    echo ================================================================
    echo.
    echo Please try:
    echo   1. python -m pip install --upgrade pip
    echo   2. Run this script again
)
echo.
pause
