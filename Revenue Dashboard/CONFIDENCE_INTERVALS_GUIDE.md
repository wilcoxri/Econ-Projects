# Confidence Intervals Guide

## Overview

Your revenue dashboard now includes confidence intervals (uncertainty bands) around all forecasts, helping you understand the range of possible outcomes.

## What Are Confidence Intervals?

A confidence interval shows the range where the actual value is likely to fall.

**Example:**
- Forecast: $100M
- 80% Confidence Interval: $95M - $105M
- **Meaning:** We're 80% confident the actual revenue will be between $95M and $105M

## Forecast Methods with Confidence Intervals

### 1. Growth-Adjusted Prior Year (Default)
**Confidence interval based on:** Historical volatility of year-over-year growth rates

**How it's calculated:**
1. Looks at YoY growth rate variations from 2022→2023, 2023→2024, 2024→2025
2. Calculates standard deviation of these growth rates
3. Uses statistical theory (normal distribution) to create bands

**Interpretation:**
- Narrow bands = Stable, predictable revenue growth
- Wide bands = Volatile revenue with uncertain growth

**When bands widen:**
- Historical growth rates vary significantly
- Economic conditions are changing
- Revenue source is becoming less predictable

---

### 2. Bayesian Structural Time Series
**Confidence interval based on:** Bayesian credible intervals

**How it's calculated:**
1. Decomposes revenue into trend and seasonal components
2. Measures residual uncertainty (forecast errors)
3. Adds parameter uncertainty (how well we know the adjustment factor)
4. Combines these using Bayesian probability theory

**Interpretation:**
- These are "credible intervals" (Bayesian term)
- 80% credible interval = 80% probability actual value is in this range
- Accounts for multiple sources of uncertainty

**Unique features:**
- Bands may widen over time (more uncertainty further out)
- Adapts to changes in revenue patterns
- More sophisticated uncertainty quantification

---

## Using Confidence Intervals

### In the Dashboard

**Adjusting the Confidence Level:**
1. Go to sidebar → Forecast Options
2. Use the "Confidence Interval" slider
3. Choose from 50% to 95%

**Recommended settings:**
- **80% (Default):** Standard for government forecasting
- **90%:** More conservative, wider bands
- **95%:** Very conservative, widest bands
- **50%:** Narrow bands, less certainty

### Visual Representation

On the Revenue Trends chart:
- **Solid line** = Actual historical data
- **Dashed line** = Forecast (median/most likely value)
- **Shaded area** = Confidence interval

**Example visualization:**
```
Revenue ($M)
    |
120 |                         ╱────── Upper bound (105M)
    |                    ╱────
100 |              ╱────  Forecast (100M)
    |         ╱────
 80 | ────────         ─────── Lower bound (95M)
    |___________________________
        Jul    Oct    Jan    Apr
```

---

## Practical Applications

### 1. Budget Planning

**Conservative Approach:**
Use the **lower bound** for revenue projections
- Protects against shortfalls
- Safer budget assumptions

**Example:**
- Forecast: $500M
- 80% CI: $475M - $525M
- **Budget on:** $475M (lower bound)

### 2. Risk Assessment

**Understand downside risk:**
- Lower bound = Pessimistic scenario
- Upper bound = Optimistic scenario
- Difference = Risk/uncertainty

**Example:**
- Sales Tax forecast: $1,000M ± $50M
- Oil & Gas forecast: $200M ± $80M
- **Conclusion:** Oil & Gas more uncertain (40% range vs 5%)

### 3. Scenario Planning

**Create multiple scenarios:**

| Scenario | Probability | Revenue Estimate |
|----------|-------------|------------------|
| Optimistic | 10% above upper bound | $550M |
| Upper Bound | 90% confidence | $525M |
| Most Likely | Forecast | $500M |
| Lower Bound | 90% confidence | $475M |
| Pessimistic | 10% below lower bound | $450M |

### 4. Communication to Decision Makers

**Instead of saying:**
"Revenue will be $500M"

**Say:**
"We forecast $500M with 80% confidence between $475M and $525M"

**Benefits:**
- More honest about uncertainty
- Shows you've considered risks
- Allows informed decision-making

---

## Understanding Confidence Levels

### What Different Levels Mean

**50% Confidence Interval:**
- Narrow bands
- 50-50 chance actual is in range
- Not very useful for planning

**80% Confidence Interval (Recommended):**
- Standard for government forecasts
- Good balance of precision and coverage
- 80% chance actual is in range

**90% Confidence Interval:**
- Wider bands
- More conservative
- 90% chance actual is in range

**95% Confidence Interval:**
- Very wide bands
- Extremely conservative
- 95% chance actual is in range

### Trade-offs

**Narrower intervals (50-70%):**
✓ More precise forecasts
✓ Easier to plan around
− Higher risk of being wrong
− May underestimate uncertainty

**Wider intervals (90-95%):**
✓ More likely to capture actual
✓ Better for risk management
− Less precise for planning
− May overestimate uncertainty

**Sweet spot: 80%**
- Used by most economic forecasters
- Good for government budgeting
- Balances precision and safety

---

## Comparing Methods

### Growth-Adjusted Intervals
- Based on historical patterns
- Reflects actual past volatility
- Simple and transparent
- Good for stable revenue sources

### BSTS Intervals
- Bayesian probability framework
- More sophisticated uncertainty
- Adapts to structural changes
- Better for complex patterns

**Which to use?**
- For most purposes: **Growth-Adjusted** (simpler, well-tested)
- For research/analysis: **BSTS** (more comprehensive uncertainty)
- They often give similar results for stable revenue

---

## Technical Details

### Statistical Formula (Growth-Adjusted)

```
Confidence Interval = Forecast ± (Z-score × σ)

Where:
- Z-score depends on confidence level:
  * 50%: 0.67
  * 80%: 1.28
  * 90%: 1.64
  * 95%: 1.96
- σ = standard deviation of historical growth rates
```

### Bayesian Formula (BSTS)

```
Credible Interval = Forecast ± (Z-score × √(σ²obs + σ²param))

Where:
- σ²obs = observation/residual uncertainty
- σ²param = parameter estimation uncertainty
- Combined using Bayesian posterior distribution
```

---

## Common Questions

**Q: Why do the bands get wider over time in BSTS?**
A: Uncertainty compounds. The further into the future we forecast, the less certain we are. BSTS reflects this naturally.

**Q: Can actual revenue fall outside the confidence interval?**
A: Yes! An 80% CI means there's a 20% chance the actual will be outside. That's normal.

**Q: Should I always use the conservative (lower bound) estimate?**
A: Depends on your risk tolerance. For budgeting, lower bound is safer. For revenue tracking, use the forecast.

**Q: Why are confidence intervals different for different revenue types?**
A: Different revenue sources have different volatility. Stable sources (like sales tax) have narrower bands than volatile ones (like oil & gas).

**Q: Do confidence intervals account for recessions or policy changes?**
A: No. They assume future uncertainty matches past patterns. Major changes require judgment adjustments.

**Q: How do I explain this to non-technical stakeholders?**
A: "Instead of saying revenue will be exactly $X, we're saying it will very likely be between $Y and $Z."

**Q: Which confidence level should I report to the legislature?**
A: 80% is standard for government forecasting. Some states also report 90% for extra conservatism.

---

## Best Practices

### 1. Always Show Uncertainty
Don't just report the forecast — show the range

### 2. Match Confidence Level to Use Case
- Budget planning: 80-90%
- Ongoing monitoring: 80%
- Risk assessment: 90-95%

### 3. Update as Data Arrives
As actual data comes in:
- Recalculate forecasts
- See if actuals fall within intervals
- Adjust if consistently outside

### 4. Consider Multiple Revenue Sources
Aggregate uncertainty doesn't simply add:
- Some revenues move together (correlated)
- Some offset each other (diversification)
- Total uncertainty may be less than sum

### 5. Document Assumptions
Always note:
- Confidence level used
- Method (Growth-Adjusted or BSTS)
- Any manual adjustments made
- Date of forecast

---

## Example: Presenting to Decision Makers

**Slide 1: Point Forecast**
"FY 2026 Sales Tax forecast: $1,200M"

**Slide 2: With Uncertainty**
"FY 2026 Sales Tax forecast: $1,200M
80% confidence interval: $1,150M - $1,250M"

**Slide 3: Interpretation**
"We're 80% confident actual revenue will be between $1,150M and $1,250M
- Budget conservatively on: $1,150M (lower bound)
- Most likely outcome: $1,200M
- Upside scenario: $1,250M"

**Slide 4: Risk Statement**
"There's a 10% chance revenue will be below $1,150M
And a 10% chance it will be above $1,250M
This reflects normal economic uncertainty"

---

## Further Reading

**Government Forecasting Standards:**
- GAO: "Fiscal Outlook" (uses 80% confidence intervals)
- CBO: "Budget and Economic Outlook" (shows ranges)
- State examples: California DOF, New York Division of Budget

**Statistical Background:**
- "Forecasting: Principles and Practice" by Hyndman & Athanasopoulos
- "The Signal and the Noise" by Nate Silver
- "Superforecasting" by Philip Tetlock

**Bayesian Approach:**
- "Bayesian Data Analysis" by Gelman et al.
- "Statistical Rethinking" by Richard McElreath
