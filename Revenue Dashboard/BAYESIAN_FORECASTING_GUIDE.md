# Bayesian Forecasting Methods Guide

## Overview

Your dashboard now includes advanced Bayesian forecasting methods alongside the proven Growth-Adjusted Prior Year approach.

## Available Forecast Methods

### 1. Growth-Adjusted Prior Year (Default - Recommended)
**Type:** Traditional statistical method
**Best for:** Most state revenue forecasting scenarios

**How it works:**
- Takes prior year's seasonal pattern
- Applies current year-over-year growth rate
- Simple, transparent, and proven accurate (won the comparison test!)

**When to use:**
- Default choice for most situations
- When you need to explain methodology to legislators
- When current growth trends are stable

---

### 2. Prophet (Bayesian)
**Type:** Bayesian time series model
**Created by:** Facebook (Meta)

**How it works:**
- Bayesian additive regression model
- Automatically detects seasonal patterns
- Fits trend, seasonality, and holiday effects
- Provides uncertainty estimates (credible intervals)

**Advantages:**
- Handles missing data and outliers gracefully
- Adapts to changing trends
- Provides confidence bands
- Widely used in industry

**When to use:**
- When you want uncertainty estimates
- When seasonal patterns are complex
- When you need to show high/low scenarios
- For presentation to technical audiences

**Requirements:**
- Minimum 30 days of actual data
- Prophet package installed

---

### 3. Bayesian Structural Time Series (BSTS)
**Type:** State space Bayesian model
**Complexity:** Advanced

**How it works:**
- Decomposes revenue into structural components:
  - Local level (base revenue)
  - Trend (growth/decline)
  - Seasonal pattern
- Uses Bayesian updating as new data arrives
- Adapts to structural changes

**Advantages:**
- Most flexible approach
- Can detect changepoints
- Bayesian credible intervals
- Handles complex patterns

**When to use:**
- When you suspect structural changes in revenue
- When growth rate is accelerating/decelerating
- For research and deep analysis
- When other methods show poor fit

**Requirements:**
- Minimum 30 days of actual data
- scipy package installed
- Prior year data for seasonal pattern

---

## Installation

### Quick Install (Recommended)
Double-click: `UPDATE_PACKAGES.bat`

This installs:
- scipy (for BSTS)
- prophet (for Prophet)

Takes 3-5 minutes.

### Manual Install
```powershell
cd C:\Users\rwilcox\Desktop
python -m pip install scipy prophet
```

---

## Using Bayesian Methods

### In the Dashboard

1. **Open Forecast Options** (left sidebar)
2. **Check "Show Forecast"**
3. **Select your method:**
   - Growth-Adjusted Prior Year
   - Prophet (Bayesian)
   - Bayesian Structural Time Series
4. **View forecast** (dashed line on Revenue Trends chart)

### Interpreting Results

**Growth-Adjusted:**
- Shows single forecast line
- Displays YoY growth rate used
- Most straightforward

**Prophet:**
- Shows forecast line (median prediction)
- May show confidence bands (in future updates)
- Look for smooth seasonal patterns

**BSTS:**
- Shows forecast line
- Adapts to recent trend changes
- May differ from simple growth-adjusted if structure is changing

---

## Comparison with Traditional Method

### Growth-Adjusted Prior Year
✓ Simple and explainable
✓ Won the accuracy test
✓ No dependencies required
✓ Fast computation
− No uncertainty estimates
− Assumes constant growth

### Prophet (Bayesian)
✓ Provides uncertainty intervals
✓ Handles complex seasonality
✓ Industry standard
✓ Robust to outliers
− Requires installation
− More complex to explain
− Slightly slower

### BSTS
✓ Most flexible
✓ Detects structural changes
✓ Bayesian credibility
✓ Advanced diagnostics
− Most complex
− Requires expertise to interpret
− Computationally intensive

---

## Practical Recommendations

### For Routine Monitoring
**Use:** Growth-Adjusted Prior Year
- Fast, accurate, easy to explain
- Already validated as best performer

### For Budget Planning
**Use:** Prophet (Bayesian)
- Get confidence intervals for scenarios
- Show legislature: "80% confident revenue will be $X-$Y"
- More defensible than point estimates

### For Economic Research
**Use:** BSTS
- Understand structural shifts
- Analyze policy impacts
- Academic rigor

### For Presentations
**Compare all three:**
- Show consensus (all methods agree)
- Show range of possibilities
- Demonstrate due diligence

---

## Technical Details

### Bayesian Approach Benefits

1. **Uncertainty Quantification**
   - Not just "revenue will be $100M"
   - But "95% credible interval: $95M-$105M"

2. **Incorporating Prior Knowledge**
   - Uses historical patterns as priors
   - Updates beliefs with new data
   - Balances past and present

3. **Probabilistic Forecasts**
   - Full posterior distribution
   - Can calculate risk metrics
   - Better for decision-making under uncertainty

### Model Selection Criteria

**Use Growth-Adjusted when:**
- Current growth is stable
- Simple explanation needed
- Fast results required

**Use Prophet when:**
- Need uncertainty bounds
- Seasonality is complex
- Want industry-standard method

**Use BSTS when:**
- Structural changes suspected
- Advanced analysis needed
- Research purposes

---

## Troubleshooting

### "Prophet not installed" error
Run: `python -m pip install prophet`
Or: Double-click `UPDATE_PACKAGES.bat`

### "scipy not available" warning
BSTS will fall back to simpler Bayesian approach
To fix: Run `python -m pip install scipy`

### Prophet is slow
- Normal for first forecast
- Subsequent forecasts are cached
- Consider using Growth-Adjusted for routine work

### Forecasts look unrealistic
- Try different method
- Check data quality
- Verify current growth rate is sustainable
- Consider external factors not in model

---

## Bayesian Statistics Primer

**What is Bayesian?**
- Statistical approach using Bayes' theorem
- Combines prior beliefs with observed data
- Updates probabilities as evidence accumulates

**Why Bayesian for forecasting?**
- Natural framework for uncertainty
- Incorporates expert knowledge
- Flexible model structures
- Interpretable probability statements

**Key Concepts:**

**Prior:** What we believe before seeing data
- Example: Historical revenue patterns

**Likelihood:** What the data tells us
- Example: Current year observations

**Posterior:** Updated beliefs after seeing data
- Example: Forecast incorporating both

---

## References

### Prophet
- Paper: Taylor & Letham (2018) "Forecasting at Scale"
- GitHub: facebook/prophet
- Used by: Facebook, Lyft, Uber, many others

### Bayesian Structural Time Series
- Paper: Scott & Varian (2014) "Predicting the Present with Bayesian Structural Time Series"
- Used by: Google, academic research
- R package: bsts

### General Bayesian Forecasting
- Book: "Forecasting: Principles and Practice" by Hyndman & Athanasopoulos
- Journal: International Journal of Forecasting

---

## Questions?

**Q: Should I always use Bayesian methods?**
A: No. Growth-Adjusted won your comparison test. Use Bayesian when you need uncertainty estimates or have complex patterns.

**Q: Are Bayesian forecasts more accurate?**
A: Not necessarily. They provide uncertainty quantification, which is different from accuracy. Your test showed Growth-Adjusted was most accurate.

**Q: Which Bayesian method should I use?**
A: Start with Prophet - it's well-tested and provides good uncertainty estimates. Use BSTS for research.

**Q: Can I combine methods?**
A: Yes! The dashboard can show multiple forecasts. Compare them to understand range of possibilities.

**Q: What's the computational cost?**
A: Prophet: ~2-5 seconds. BSTS: ~1-3 seconds. Growth-Adjusted: <0.1 seconds.

**Q: Do I need to understand Bayesian statistics?**
A: Not required for basic use. Helpful for interpreting uncertainty and making method choices.
