@echo off
echo ================================================================
echo Revenue Forecast Model Comparison
echo ================================================================
echo.
echo This will test different forecasting methods on your data
echo and create visualizations showing which performs best.
echo.
echo The analysis uses 2024 data to test accuracy, comparing
echo forecasts made at mid-year against actual values.
echo.
echo NOTE: If this is your first time running this, you may need to
echo       install required packages first by running:
echo       install_comparison_packages.bat
echo.
pause
echo.
echo Running comparison...
echo.
cd /d "%~dp0"
python forecast_comparison.py
echo.
echo.
echo ================================================================
echo Check the HTML files created for interactive visualizations!
echo ================================================================
echo.
pause
