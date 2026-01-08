@echo off
echo Updating Dashboard Packages...
echo.
echo Installing packages for advanced forecasting features:
echo   - scipy (for Bayesian Structural Time Series with confidence intervals)
echo.
echo This may take 1-2 minutes...
echo.
cd /d "%~dp0"

python -m pip install scipy --upgrade

echo.
echo Update complete!
echo.
echo You can now use BSTS forecasting method with confidence bands.
echo.
pause
