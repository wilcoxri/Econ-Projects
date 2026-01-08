# Revenue Forecasting Feature Guide

## Overview

The dashboard now includes forecasting capabilities that predict future revenue for the remainder of the fiscal year based on historical patterns.

## Setup

Before using the forecasting feature, you need to install additional packages:

### Option 1: Run the update script
Double-click `UPDATE_PACKAGES.bat` on your Desktop

### Option 2: Manual installation
```powershell
cd C:\Users\rwilcox\Desktop
python -m pip install scikit-learn numpy
```

## How to Use

1. **Start the dashboard** - Double-click `run_dashboard.bat`

2. **Enable forecasting** - In the left sidebar under "Forecast Options":
   - Check "Show Forecast" to enable forecast lines
   - Select your preferred forecast method
   - Choose which years should show forecasts (default: 2026)

## Forecast Methods

### 1. Growth-Adjusted Prior Year (Recommended - Default)
**How it works:**
1. Calculates your current year-over-year (YoY) growth rate by comparing the latest actual data point to the same day last year
2. Takes last year's pattern for the remaining days of the fiscal year
3. Applies your current YoY growth rate to those values

**Best for:**
- Cumulative revenue data (like your dataset)
- When current growth trends are expected to continue
- Most accurate for typical state revenue forecasting

**Example:** If withholding on Jan 6, 2026 is $500M and was $483.6M on Jan 6, 2025 (3.4% growth), the forecast will take all future days from 2025 and increase them by 3.4%.

**Visual feedback:** The dashboard shows the YoY growth rate being applied for each revenue type.

### 2. Linear Trend
**How it works:** Fits a straight line to the current year's actual data and projects it forward.

**Best for:**
- When you see a clear acceleration or deceleration in growth
- Short-term forecasts when recent momentum is most important
- Identifying if current trend differs from historical patterns

**Note:** Requires at least 10 days of actual data to generate a forecast.

### 3. Historical Average
**How it works:** For each future day, calculates the average revenue from the same day in previous years.

**Best for:**
- When current year data is limited or unreliable
- Cross-checking other forecast methods
- Very stable revenue sources with no growth trend

**Note:** May underestimate if there's consistent growth, or overestimate if there's decline.

## Understanding the Forecast Display

- **Solid lines** = Actual revenue data
- **Dashed lines** = Forecasted revenue
- Forecasts only appear for future dates (after the last actual data point)
- Hover over lines to see exact values

## Customization Options

### Select Historical Years for Forecasting
By default, the forecast uses all years you've selected EXCEPT the forecast year itself.

**Example:** If you're forecasting 2026 and have selected years 2022-2026:
- Forecast will use 2022, 2023, 2024, and 2025 as historical data
- 2026 shows actual data where available, then forecast

### Choose Forecast Years
- Default: Only 2026 shows forecast
- You can add 2025 if you want to forecast the rest of FY 2025
- Forecast starts where actual data ends

## Tips for Decision Makers

### Comparing Scenarios
1. Try different forecast methods to see a range of possibilities
2. Historical Average tends to be most conservative
3. Linear Trend responds quickly to recent changes
4. Year-over-Year Growth captures momentum

### Evaluating Forecast Accuracy
As the fiscal year progresses:
1. Keep the forecast enabled as actual data comes in
2. Compare forecast vs actual to see which method is most accurate
3. Adjust your forecast method selection accordingly

### Revenue Planning
- Use Historical Average for budget planning (conservative)
- Use Linear Trend when you see strong momentum
- Compare multiple methods to establish high/low ranges

## Technical Details

### Fiscal Year
The dashboard assumes a July 1 - June 30 fiscal year based on your data structure.

### Data Requirements
- Historical Average: At least 1 prior year with data
- Linear Trend: At least 10 days of actual data in the current year
- Year-over-Year Growth: At least 2 prior years with data

### Forecast Limitations
- Forecasts do not account for:
  - Policy changes
  - Economic shocks
  - New revenue sources
  - One-time adjustments
- Always apply professional judgment to forecast results

## Troubleshooting

**No forecast lines appear:**
- Make sure "Show Forecast" is checked
- Verify you've selected at least one year in "Years to Forecast"
- Check that the selected year is also in "Select Years to Compare"
- Ensure there's actual data available to forecast from

**Forecast looks unrealistic:**
- Try a different forecast method
- Check for data quality issues in historical years
- Consider if recent data is typical or anomalous

**Error messages:**
- Make sure you installed scikit-learn and numpy
- Restart the dashboard after installing new packages

## Questions or Issues?

The forecasting feature is designed to assist with revenue planning and analysis. Always review forecasts critically and adjust based on your knowledge of economic conditions, policy changes, and other factors that the model cannot predict.
