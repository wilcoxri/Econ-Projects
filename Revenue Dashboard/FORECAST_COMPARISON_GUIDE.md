# Forecast Model Comparison Guide

## What This Does

This analysis tests different forecasting methods on your actual historical data to see which one would have been most accurate.

**The Test:**
- Uses your 2024 data as a "test case"
- Pretends we're at day 180 (mid-fiscal year - January 2024)
- Each method forecasts the rest of the year
- Compares forecasts to actual 2024 values
- Shows which method was most accurate

## How to Run

**Option 1:** Double-click `run_forecast_comparison.bat`

**Option 2:** From PowerShell:
```powershell
cd C:\Users\rwilcox\Desktop
python forecast_comparison.py
```

## Methods Being Tested

### 1. Growth-Adjusted Prior Year (Current Dashboard Method)
- Takes prior year pattern
- Applies current YoY growth rate
- Simple and intuitive

### 2. Linear Trend
- Fits straight line to year-to-date data
- Projects forward
- Good for strong trends

### 3. Historical Average
- Averages same day from multiple prior years
- Conservative approach
- Smooths out volatility

### 4. Exponential Smoothing
- Weights recent data more heavily
- Adapts to changing patterns
- Classic statistical method

### 5. Prophet (Bayesian) *If installed*
- Facebook's forecasting tool
- Handles seasonality automatically
- Provides uncertainty intervals
- **To install:** `python -m pip install prophet`

### 6. Ensemble
- Averages all available methods
- Reduces risk of any single model being wrong
- Often most robust

## Understanding the Output

### Terminal Output

You'll see accuracy metrics for each revenue type:

```
Method                          MAE         MAPE    Final Error
---------------------------------------------------------------
Growth-Adjusted            $15.32M       3.24%        +2.50%
Linear Trend               $18.45M       3.89%        -1.20%
Prophet                    $12.10M       2.55%        +0.80%
Ensemble                   $13.22M       2.79%        +1.10%
```

**MAE (Mean Absolute Error):** Average dollar error across all days
- Lower is better
- Shows typical day-to-day error

**MAPE (Mean Absolute Percentage Error):** Average percentage error
- Lower is better
- Best overall metric for comparing methods
- **< 5% = Excellent**
- **5-10% = Good**
- **> 10% = Needs improvement**

**Final Error:** Error in end-of-year forecast
- Important for budget planning
- Positive = overestimated, Negative = underestimated

### HTML Visualizations

The script creates interactive HTML files (one per revenue type):
- `forecast_comparison_Sales_and_Use_Tax.html`
- `forecast_comparison_Withholding.html`
- `forecast_comparison_Oil_and_Gas_Severance_Tax.html`

**Top Chart:**
- Black line = Actual historical data (before forecast)
- Red solid line = Actual values (what we're trying to predict)
- Colored dashed lines = Different forecast methods
- Closer to red line = more accurate

**Bottom Chart:**
- Shows forecast errors over time
- Line at zero = perfect forecast
- See which methods consistently over/under predict

## Interpreting Results

### If Growth-Adjusted is Best:
✓ Your current dashboard method is already optimal!
- No need to add complexity
- Keep what you have

### If Prophet is Best:
Consider adding it if:
- Improvement is significant (>1% MAPE reduction)
- You want uncertainty intervals
- You're comfortable with more complex models

**Trade-off:** More accurate, but requires additional dependency

### If Ensemble is Best:
Highly recommended to add:
- More robust than single methods
- Reduces risk of being wrong
- No new dependencies needed

**Trade-off:** Slightly more complex to explain

### If Linear Trend is Best:
Your revenue may be accelerating/decelerating:
- Consider economic factors
- May indicate shift from historical patterns
- Good for short-term forecasts

## What to Look For

### Good Signs:
- ✓ MAPE < 5% for most methods
- ✓ Small spread between methods
- ✓ Errors distributed evenly (not all positive or negative)
- ✓ Ensemble performs well

### Warning Signs:
- ⚠ MAPE > 10%
- ⚠ Large differences between methods
- ⚠ Consistent over or under-prediction
- ⚠ Errors increasing over time

If you see warning signs, it may indicate:
- Structural changes in revenue patterns
- Need for external variables (economic indicators)
- Data quality issues

## Recommendations by Use Case

### For Budget Planning (Conservative):
**Recommended:** Ensemble or Historical Average
- Tends to smooth out extremes
- Less likely to overestimate

### For Revenue Tracking (Accurate):
**Recommended:** Best MAPE method
- Most accurate on average
- Good for ongoing monitoring

### For Scenario Planning:
**Recommended:** Prophet (if available)
- Provides confidence intervals
- Shows range of possible outcomes

### For Simplicity:
**Recommended:** Growth-Adjusted (current)
- Easy to explain
- Transparent methodology
- Good enough for most purposes

## Next Steps

After reviewing the comparison:

1. **Identify the best method** for your needs based on MAPE and use case

2. **Review visualizations** to understand how methods differ

3. **Decide if you want to add new methods** to the dashboard
   - If Prophet is clearly better → Install and add it
   - If Ensemble is better → Add it (no new dependencies)
   - If current method is best → No changes needed

4. **Let me know** which methods you'd like to add, and I'll integrate them into your dashboard

## Technical Notes

### Why Test on 2024?
- Most recent complete year with data
- Mimics real forecasting scenario
- Can validate against actual outcomes

### Why Day 180?
- Mid-fiscal year (January)
- Enough historical data for models to work
- Enough future data to test accuracy
- Typical time for mid-year forecasts

### Limitations
- Past performance ≠ future results
- Cannot predict policy changes, economic shocks
- Assumes patterns continue
- Single year test may not capture all scenarios

## Questions?

Common questions after running the analysis:

**Q: Method X has lowest MAE but Method Y has lowest MAPE. Which is better?**
A: MAPE is generally more useful because it's percentage-based and comparable across revenue types.

**Q: Why are some methods missing for certain revenue types?**
A: Insufficient data or method requirements not met (e.g., Linear Trend needs 10+ days)

**Q: Should I always use the most accurate method?**
A: Not necessarily. Consider trade-offs: simplicity, explainability, robustness, and whether improvement is meaningful.

**Q: Can I test on multiple years?**
A: Yes! Edit the script to change TEST_YEAR and HISTORICAL_YEARS variables.

**Q: What if all methods have high errors?**
A: May need external variables (unemployment, oil prices, etc.) or more sophisticated models. Let me know and I can help.
