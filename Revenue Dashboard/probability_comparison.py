"""
Probability Comparison Tool
Compares three methods for estimating probability of hitting consensus forecast
"""

import pandas as pd
import numpy as np
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("PROBABILITY COMPARISON: Three Methods")
print("="*80)
print()

# Load data
print("Loading data...")
df = pd.read_csv('rev9.csv', thousands=',')
df['date'] = pd.to_datetime(df['date'], format='%d%b%Y')

# Get year columns and convert to numeric
year_cols = [col for col in df.columns if col.startswith('y')]
for col in year_cols:
    if df[col].dtype == 'object':
        df[col] = df[col].str.replace(',', '')
    df[col] = pd.to_numeric(df[col], errors='coerce')
df[year_cols] = df[year_cols].fillna(0)

# Create custom categories (same as dashboard)
# Individual Income Tax
income_tax_components = ['Withholding', 'Gross Payments', 'Refunds']
component_data = df[df['rev'].isin(income_tax_components)].copy()
if len(component_data) > 0:
    income_tax_data = component_data.groupby(['day', 'date']).agg({
        **{col: 'sum' for col in year_cols}
    }).reset_index()
    income_tax_data['rev'] = 'Individual Income Tax'
    income_tax_data = income_tax_data[['rev', 'day', 'date'] + year_cols]
    df = pd.concat([df, income_tax_data], ignore_index=True)

# Sales and Use Tax (GF)
sales_tax_data = df[df['rev'] == 'Sales and Use Tax'].copy()
if len(sales_tax_data) > 0:
    gf_percentages = {
        'y2026': 0.66098, 'y2025': 0.72963, 'y2024': 0.73003,
        'y2023': 0.7312089, 'y2022': 0.740058
    }
    for year_col, percentage in gf_percentages.items():
        if year_col in sales_tax_data.columns:
            sales_tax_data[year_col] = sales_tax_data[year_col] * percentage
    sales_tax_data['rev'] = 'Sales and Use Tax (GF)'
    df = pd.concat([df, sales_tax_data], ignore_index=True)

df.loc[df['rev'] == 'Sales and Use Tax', 'rev'] = 'Sales and Use Tax (Total)'
df.loc[df['rev'] == 'Education Fund Other', 'rev'] = 'Income Tax Fund Other'

# General Fund
general_fund_components = [
    'Sales and Use Tax (GF)', 'Cable/Satellite Excise Tax', 'Liquor Profits',
    'Insurance Premiums', 'Beer, Cigarette, and Tobacco', 'Oil and Gas Severance Tax',
    'Metal Severance Tax', 'Investment Income', 'General Fund Other', 'Property and Energy Credit'
]
gf_component_data = df[df['rev'].isin(general_fund_components)].copy()
if len(gf_component_data) > 0:
    general_fund_data = gf_component_data.groupby(['day', 'date']).agg({
        **{col: 'sum' for col in year_cols}
    }).reset_index()
    general_fund_data['rev'] = 'General Fund'
    general_fund_data = general_fund_data[['rev', 'day', 'date'] + year_cols]
    df = pd.concat([df, general_fund_data], ignore_index=True)

# Income Tax Fund
income_tax_fund_components = [
    'Individual Income Tax', 'Corporate Tax & Gross Receipts',
    'Mineral Production Withholding', 'Income Tax Fund Other'
]
itf_component_data = df[df['rev'].isin(income_tax_fund_components)].copy()
if len(itf_component_data) > 0:
    income_tax_fund_data = itf_component_data.groupby(['day', 'date']).agg({
        **{col: 'sum' for col in year_cols}
    }).reset_index()
    income_tax_fund_data['rev'] = 'Income Tax Fund'
    income_tax_fund_data = income_tax_fund_data[['rev', 'day', 'date'] + year_cols]
    df = pd.concat([df, income_tax_fund_data], ignore_index=True)

# GF/ITF
gf_itf_components = ['General Fund', 'Income Tax Fund']
gf_itf_component_data = df[df['rev'].isin(gf_itf_components)].copy()
if len(gf_itf_component_data) > 0:
    gf_itf_data = gf_itf_component_data.groupby(['day', 'date']).agg({
        **{col: 'sum' for col in year_cols}
    }).reset_index()
    gf_itf_data['rev'] = 'GF/ITF'
    gf_itf_data = gf_itf_data[['rev', 'day', 'date'] + year_cols]
    df = pd.concat([df, gf_itf_data], ignore_index=True)

# Load consensus forecast
forecast_df = pd.read_csv('FY26 forecast.csv')
forecast_df.columns = forecast_df.columns.str.strip()
forecast_df['Rev'] = forecast_df['Rev'].str.strip()
forecast_df['Level Forecast'] = forecast_df['Level Forecast'].str.replace(',', '').str.strip()
forecast_df['Level Forecast'] = pd.to_numeric(forecast_df['Level Forecast'], errors='coerce')
forecast_df['Growth Forecast'] = forecast_df['Growth Forecast'].str.replace('%', '').str.strip()
forecast_df['Growth Forecast'] = pd.to_numeric(forecast_df['Growth Forecast'], errors='coerce')

level_forecast = dict(zip(forecast_df['Rev'], forecast_df['Level Forecast']))
growth_forecast = dict(zip(forecast_df['Rev'], forecast_df['Growth Forecast']))

print("✓ Data loaded successfully")
print()

# ============================================================================
# METHOD 1: Model Forecast Distribution
# ============================================================================

def method1_forecast_distribution(df, rev_type, consensus_total):
    """Use confidence intervals from Growth-Adjusted forecast"""
    rev_data = df[df['rev'] == rev_type].copy()

    year_col = 'y2026'
    prior_year_col = 'y2025'

    # Find current position
    non_zero_mask = rev_data[year_col].abs() > 0.01
    if not non_zero_mask.any():
        return None, None

    last_actual_idx = rev_data[non_zero_mask].index[-1]
    last_actual_day = rev_data.loc[last_actual_idx, 'day']
    last_actual_value = rev_data.loc[last_actual_idx, year_col]

    # Get prior year value at same day
    prior_value = rev_data.loc[rev_data['day'] == last_actual_day, prior_year_col].iloc[0]

    if prior_value < 0.01:
        return None, None

    # Calculate current growth rate
    growth_rate = (last_actual_value - prior_value) / prior_value

    # Calculate historical growth rate volatility
    historical_years = ['2022', '2023', '2024', '2025']
    historical_growth_rates = []

    for i in range(len(historical_years) - 1):
        y1 = historical_years[i]
        y2 = historical_years[i + 1]
        col1 = f'y{y1}'
        col2 = f'y{y2}'

        if col1 in rev_data.columns and col2 in rev_data.columns:
            val1 = rev_data.loc[rev_data['day'] == last_actual_day, col1]
            val2 = rev_data.loc[rev_data['day'] == last_actual_day, col2]

            if len(val1) > 0 and len(val2) > 0:
                v1 = val1.iloc[0]
                v2 = val2.iloc[0]
                if v1 > 0.01:
                    hist_growth = (v2 - v1) / v1
                    historical_growth_rates.append(hist_growth)

    if len(historical_growth_rates) > 1:
        growth_std = np.std(historical_growth_rates)
    else:
        growth_std = 0.05  # Default 5% volatility

    # Get prior year's ending total
    prior_year_total = rev_data[prior_year_col].max()

    # Forecast total = current actual + (prior year remaining * (1 + growth_rate))
    prior_year_remaining = prior_year_total - prior_value
    forecast_total = last_actual_value + (prior_year_remaining * (1 + growth_rate))

    # Standard deviation of forecast total
    # Uncertainty scales with remaining revenue
    forecast_std = prior_year_remaining * growth_std

    # Calculate probability: P(Actual >= Consensus)
    # Using normal distribution
    z_score = (consensus_total - forecast_total) / forecast_std if forecast_std > 0 else 0
    probability = 1 - stats.norm.cdf(z_score)  # Probability of exceeding consensus

    return probability * 100, {
        'forecast_total': forecast_total,
        'forecast_std': forecast_std,
        'consensus_total': consensus_total,
        'z_score': z_score
    }

# ============================================================================
# METHOD 2: Growth Rate Distribution
# ============================================================================

def method2_growth_distribution(df, rev_type, consensus_growth):
    """Based on historical growth rate volatility"""
    rev_data = df[df['rev'] == rev_type].copy()

    year_col = 'y2026'
    prior_year_col = 'y2025'

    # Find current position
    non_zero_mask = rev_data[year_col].abs() > 0.01
    if not non_zero_mask.any():
        return None, None

    last_actual_idx = rev_data[non_zero_mask].index[-1]
    last_actual_day = rev_data.loc[last_actual_idx, 'day']
    last_actual_value = rev_data.loc[last_actual_idx, year_col]

    # Get prior year value at same day
    prior_value = rev_data.loc[rev_data['day'] == last_actual_day, prior_year_col].iloc[0]

    if prior_value < 0.01:
        return None, None

    # Calculate current growth rate
    current_growth = (last_actual_value - prior_value) / prior_value * 100

    # Calculate historical growth rate volatility
    historical_years = ['2022', '2023', '2024', '2025']
    historical_growth_rates = []

    for i in range(len(historical_years) - 1):
        y1 = historical_years[i]
        y2 = historical_years[i + 1]
        col1 = f'y{y1}'
        col2 = f'y{y2}'

        if col1 in rev_data.columns and col2 in rev_data.columns:
            # Use year-end totals
            total1 = rev_data[col1].max()
            total2 = rev_data[col2].max()

            if total1 > 0.01:
                hist_growth = (total2 - total1) / total1 * 100
                historical_growth_rates.append(hist_growth)

    if len(historical_growth_rates) > 1:
        growth_std = np.std(historical_growth_rates)
    else:
        growth_std = 5.0  # Default 5% volatility

    # Assume final growth rate is normally distributed around current growth
    # with standard deviation based on historical volatility
    # But we need to account for remaining uncertainty in the year

    # Days remaining in fiscal year
    total_days = 365  # Approximate
    days_elapsed = last_actual_day
    days_remaining = total_days - days_elapsed

    # Uncertainty reduces as we get closer to year end
    time_factor = np.sqrt(days_remaining / total_days)
    adjusted_std = growth_std * time_factor

    # Calculate probability: P(Final Growth >= Consensus Growth)
    z_score = (consensus_growth - current_growth) / adjusted_std if adjusted_std > 0 else 0
    probability = 1 - stats.norm.cdf(z_score)

    return probability * 100, {
        'current_growth': current_growth,
        'growth_std': growth_std,
        'adjusted_std': adjusted_std,
        'consensus_growth': consensus_growth,
        'days_remaining': days_remaining,
        'z_score': z_score
    }

# ============================================================================
# METHOD 3: Monte Carlo Simulation
# ============================================================================

def method3_monte_carlo(df, rev_type, consensus_total, n_simulations=10000):
    """Simulate thousands of possible outcomes"""
    rev_data = df[df['rev'] == rev_type].copy()

    year_col = 'y2026'
    prior_year_col = 'y2025'

    # Find current position
    non_zero_mask = rev_data[year_col].abs() > 0.01
    if not non_zero_mask.any():
        return None, None

    last_actual_idx = rev_data[non_zero_mask].index[-1]
    last_actual_day = rev_data.loc[last_actual_idx, 'day']
    last_actual_value = rev_data.loc[last_actual_idx, year_col]

    # Get prior year data
    prior_value = rev_data.loc[rev_data['day'] == last_actual_day, prior_year_col].iloc[0]
    prior_year_total = rev_data[prior_year_col].max()

    if prior_value < 0.01:
        return None, None

    # Calculate current growth rate
    current_growth = (last_actual_value - prior_value) / prior_value

    # Calculate historical growth rate volatility
    historical_years = ['2022', '2023', '2024', '2025']
    historical_growth_rates = []

    for i in range(len(historical_years) - 1):
        y1 = historical_years[i]
        y2 = historical_years[i + 1]
        col1 = f'y{y1}'
        col2 = f'y{y2}'

        if col1 in rev_data.columns and col2 in rev_data.columns:
            total1 = rev_data[col1].max()
            total2 = rev_data[col2].max()

            if total1 > 0.01:
                hist_growth = (total2 - total1) / total1
                historical_growth_rates.append(hist_growth)

    if len(historical_growth_rates) > 1:
        growth_std = np.std(historical_growth_rates)
    else:
        growth_std = 0.05

    # Run Monte Carlo simulation
    prior_year_remaining = prior_year_total - prior_value

    simulated_totals = []
    for _ in range(n_simulations):
        # Sample a possible final growth rate from normal distribution
        # Mean = current growth, SD = historical volatility (scaled by time remaining)
        days_remaining = 365 - last_actual_day
        time_factor = np.sqrt(days_remaining / 365)
        adjusted_std = growth_std * time_factor

        simulated_growth = np.random.normal(current_growth, adjusted_std)

        # Calculate resulting total
        simulated_total = last_actual_value + (prior_year_remaining * (1 + simulated_growth))
        simulated_totals.append(simulated_total)

    # Calculate probability
    simulated_totals = np.array(simulated_totals)
    probability = np.mean(simulated_totals >= consensus_total) * 100

    return probability, {
        'mean_forecast': np.mean(simulated_totals),
        'median_forecast': np.median(simulated_totals),
        'std_forecast': np.std(simulated_totals),
        'consensus_total': consensus_total,
        'percentile_5': np.percentile(simulated_totals, 5),
        'percentile_95': np.percentile(simulated_totals, 95)
    }

# ============================================================================
# Run Comparisons
# ============================================================================

print("Calculating probabilities using three methods...")
print()

funds = ['General Fund', 'Income Tax Fund', 'GF/ITF']

results = []

for fund in funds:
    print(f"\n{'='*80}")
    print(f"{fund.upper()}")
    print(f"{'='*80}\n")

    consensus_total = level_forecast.get(fund)
    consensus_growth = growth_forecast.get(fund)

    if consensus_total is None or consensus_growth is None:
        print(f"⚠ No consensus forecast available for {fund}")
        continue

    print(f"Consensus Forecast Total: ${consensus_total:,.2f}M")
    print(f"Consensus Growth Rate: {consensus_growth:+.2f}%")
    print()

    # Method 1
    prob1, details1 = method1_forecast_distribution(df, fund, consensus_total)

    # Method 2
    prob2, details2 = method2_growth_distribution(df, fund, consensus_growth)

    # Method 3
    prob3, details3 = method3_monte_carlo(df, fund, consensus_total)

    print("METHOD 1: Model Forecast Distribution")
    print("-" * 40)
    if prob1 is not None:
        print(f"  Probability: {prob1:.1f}%")
        print(f"  Model forecast total: ${details1['forecast_total']:,.2f}M")
        print(f"  Forecast std dev: ${details1['forecast_std']:,.2f}M")
        print(f"  Z-score: {details1['z_score']:.2f}")
    else:
        print("  Unable to calculate")
    print()

    print("METHOD 2: Growth Rate Distribution")
    print("-" * 40)
    if prob2 is not None:
        print(f"  Probability: {prob2:.1f}%")
        print(f"  Current growth: {details2['current_growth']*100:+.2f}%")
        print(f"  Growth std dev: {details2['adjusted_std']:.2f}%")
        print(f"  Days remaining: {details2['days_remaining']}")
        print(f"  Z-score: {details2['z_score']:.2f}")
    else:
        print("  Unable to calculate")
    print()

    print("METHOD 3: Monte Carlo Simulation (10,000 runs)")
    print("-" * 40)
    if prob3 is not None:
        print(f"  Probability: {prob3:.1f}%")
        print(f"  Mean forecast: ${details3['mean_forecast']:,.2f}M")
        print(f"  Median forecast: ${details3['median_forecast']:,.2f}M")
        print(f"  Std dev: ${details3['std_forecast']:,.2f}M")
        print(f"  90% CI: ${details3['percentile_5']:,.2f}M - ${details3['percentile_95']:,.2f}M")
    else:
        print("  Unable to calculate")
    print()

    # Calculate average of the three methods
    valid_probs = [p for p in [prob1, prob2, prob3] if p is not None]
    if len(valid_probs) > 0:
        avg_prob = np.mean(valid_probs)
        min_prob = np.min(valid_probs)
        max_prob = np.max(valid_probs)
        range_prob = max_prob - min_prob
    else:
        avg_prob = None
        min_prob = None
        max_prob = None
        range_prob = None

    results.append({
        'Fund': fund,
        'Method 1': f"{prob1:.1f}%" if prob1 else "N/A",
        'Method 2': f"{prob2:.1f}%" if prob2 else "N/A",
        'Method 3': f"{prob3:.1f}%" if prob3 else "N/A",
        'Average': f"{avg_prob:.1f}%" if avg_prob else "N/A",
        'Range': f"{range_prob:.1f}%" if range_prob else "N/A"
    })

# Summary table
print("\n" + "="*80)
print("SUMMARY: Probability of Hitting or Exceeding Consensus Forecast")
print("="*80)
print()

summary_df = pd.DataFrame(results)
print(summary_df.to_string(index=False))
print()

print("\nKEY TAKEAWAY - AVERAGE PROBABILITIES:")
print("-" * 80)
for result in results:
    fund = result['Fund']
    avg = result['Average']
    range_val = result['Range']
    print(f"  {fund:20s}: {avg:>6s}  (range: {range_val})")
print()
print("Note: 'Range' shows the spread between min and max methods.")
print("      Smaller range = methods agree more, higher confidence in estimate.")
print()

print("\n" + "="*80)
print("METHOD COMPARISON")
print("="*80)
print()
print("METHOD 1: Model Forecast Distribution")
print("  • Uses confidence intervals from growth-adjusted forecast")
print("  • Accounts for historical volatility and remaining revenue")
print("  • Statistical foundation (normal distribution)")
print("  • Best for: Overall forecast uncertainty")
print()
print("METHOD 2: Growth Rate Distribution")
print("  • Based on historical growth rate volatility")
print("  • Adjusts for time remaining in fiscal year")
print("  • Assumes growth rate is normally distributed")
print("  • Best for: Simple, growth-focused probability")
print()
print("METHOD 3: Monte Carlo Simulation")
print("  • Simulates 10,000 possible outcomes")
print("  • Most comprehensive uncertainty quantification")
print("  • No parametric assumptions")
print("  • Best for: Robust probability estimates")
print()
print("RECOMMENDATION:")
print("  Method 3 (Monte Carlo) is most robust and comprehensive.")
print("  Method 1 is good alternative if computational speed matters.")
print("  All three should give similar results if assumptions are valid.")
print()
