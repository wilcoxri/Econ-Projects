"""
Revenue Forecast Model Comparison Tool

This script compares different forecasting methods on your revenue data
to help you decide which model to add to the dashboard.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

print("="*70)
print("REVENUE FORECAST MODEL COMPARISON")
print("="*70)
print()

# Check for required packages
try:
    from sklearn.linear_model import LinearRegression
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("⚠ scikit-learn not installed - Linear Trend will be skipped")
    print("  To install: python -m pip install scikit-learn")
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

# Create Individual Income Tax category by combining Withholding, Gross Payments, and Refunds
income_tax_components = ['Withholding', 'Gross Payments', 'Refunds']
component_data = df[df['rev'].isin(income_tax_components)].copy()

if len(component_data) > 0:
    income_tax_data = component_data.groupby(['day', 'date']).agg({
        **{col: 'sum' for col in year_cols}
    }).reset_index()
    income_tax_data['rev'] = 'Individual Income Tax'
    income_tax_data = income_tax_data[['rev', 'day', 'date'] + year_cols]
    df = pd.concat([df, income_tax_data], ignore_index=True)

# Create Sales and Use Tax (GF) category with year-specific percentages
sales_tax_data = df[df['rev'] == 'Sales and Use Tax'].copy()

if len(sales_tax_data) > 0:
    gf_percentages = {
        'y2026': 0.66098,
        'y2025': 0.72963,
        'y2024': 0.73003,
        'y2023': 0.7312089,
        'y2022': 0.740058
    }

    for year_col, percentage in gf_percentages.items():
        if year_col in sales_tax_data.columns:
            sales_tax_data[year_col] = sales_tax_data[year_col] * percentage

    sales_tax_data['rev'] = 'Sales and Use Tax (GF)'
    df = pd.concat([df, sales_tax_data], ignore_index=True)

# Rename "Sales and Use Tax" to "Sales and Use Tax (Total)"
df.loc[df['rev'] == 'Sales and Use Tax', 'rev'] = 'Sales and Use Tax (Total)'

# Rename "Education Fund Other" to "Income Tax Fund Other"
df.loc[df['rev'] == 'Education Fund Other', 'rev'] = 'Income Tax Fund Other'

# Create General Fund category by combining multiple revenue sources
general_fund_components = [
    'Sales and Use Tax (GF)',
    'Cable/Satellite Excise Tax',
    'Liquor Profits',
    'Insurance Premiums',
    'Beer, Cigarette, and Tobacco',
    'Oil and Gas Severance Tax',
    'Metal Severance Tax',
    'Investment Income',
    'General Fund Other',
    'Property and Energy Credit'
]

gf_component_data = df[df['rev'].isin(general_fund_components)].copy()

if len(gf_component_data) > 0:
    general_fund_data = gf_component_data.groupby(['day', 'date']).agg({
        **{col: 'sum' for col in year_cols}
    }).reset_index()
    general_fund_data['rev'] = 'General Fund'
    general_fund_data = general_fund_data[['rev', 'day', 'date'] + year_cols]
    df = pd.concat([df, general_fund_data], ignore_index=True)

# Create Income Tax Fund category by combining multiple revenue sources
income_tax_fund_components = [
    'Individual Income Tax',
    'Corporate Tax & Gross Receipts',
    'Mineral Production Withholding',
    'Income Tax Fund Other'
]

itf_component_data = df[df['rev'].isin(income_tax_fund_components)].copy()

if len(itf_component_data) > 0:
    income_tax_fund_data = itf_component_data.groupby(['day', 'date']).agg({
        **{col: 'sum' for col in year_cols}
    }).reset_index()
    income_tax_fund_data['rev'] = 'Income Tax Fund'
    income_tax_fund_data = income_tax_fund_data[['rev', 'day', 'date'] + year_cols]
    df = pd.concat([df, income_tax_fund_data], ignore_index=True)

# Create GF/ITF category by combining General Fund and Income Tax Fund
gf_itf_components = ['General Fund', 'Income Tax Fund']

gf_itf_component_data = df[df['rev'].isin(gf_itf_components)].copy()

if len(gf_itf_component_data) > 0:
    gf_itf_data = gf_itf_component_data.groupby(['day', 'date']).agg({
        **{col: 'sum' for col in year_cols}
    }).reset_index()
    gf_itf_data['rev'] = 'GF/ITF'
    gf_itf_data = gf_itf_data[['rev', 'day', 'date'] + year_cols]
    df = pd.concat([df, gf_itf_data], ignore_index=True)

print("✓ Data loaded successfully")
print()

# ============================================================================
# CONFIGURATION
# ============================================================================

# Select revenue types to analyze
REVENUE_TYPES = ['General Fund', 'Income Tax Fund', 'Individual Income Tax']

# Test configuration: Use 2024 data to forecast, compare against actual 2024
TEST_YEAR = '2024'  # Year we'll pretend to forecast
ACTUAL_YEAR_COL = 'y2024'
FORECAST_FROM_DAY = 180  # Day 180 = roughly January (midway through fiscal year)

# Historical years to use for training
HISTORICAL_YEARS = ['2021', '2022', '2023']

print(f"Test Configuration:")
print(f"  - Forecasting year: {TEST_YEAR}")
print(f"  - Using actual data through day {FORECAST_FROM_DAY}")
print(f"  - Comparing forecast vs actual for remaining days")
print(f"  - Training on historical years: {', '.join(HISTORICAL_YEARS)}")
print()

# ============================================================================
# FORECAST METHODS
# ============================================================================

def growth_adjusted_forecast(df, rev_type, test_day):
    """Current dashboard method"""
    rev_data = df[df['rev'] == rev_type].copy()

    # Get actual value at test_day
    actual_2024 = rev_data.loc[rev_data['day'] == test_day, ACTUAL_YEAR_COL].iloc[0]
    actual_2023 = rev_data.loc[rev_data['day'] == test_day, 'y2023'].iloc[0]

    if actual_2023 < 0.01:
        return None

    growth_rate = (actual_2024 - actual_2023) / actual_2023

    # Get 2023 future values and apply growth
    future_days = rev_data[rev_data['day'] > test_day].copy()
    future_2023 = future_days['y2023'].values
    forecast = future_2023 * (1 + growth_rate)

    return forecast, f"Growth: {growth_rate*100:.2f}%"


def linear_trend_forecast(df, rev_type, test_day):
    """Linear regression on year-to-date data"""
    if not SKLEARN_AVAILABLE:
        return None

    rev_data = df[df['rev'] == rev_type].copy()

    # Use data up to test_day
    train_data = rev_data[rev_data['day'] <= test_day].copy()
    train_data = train_data[train_data[ACTUAL_YEAR_COL] > 0.01]

    if len(train_data) < 10:
        return None

    X = train_data['day'].values.reshape(-1, 1)
    y = train_data[ACTUAL_YEAR_COL].values

    model = LinearRegression()
    model.fit(X, y)

    # Predict future
    future_days = rev_data[rev_data['day'] > test_day]['day'].values.reshape(-1, 1)
    forecast = model.predict(future_days)

    r2 = model.score(X, y)
    return forecast, f"R²: {r2:.3f}"


def historical_average_forecast(df, rev_type, test_day):
    """Average of historical years"""
    rev_data = df[df['rev'] == rev_type].copy()

    future_days_data = rev_data[rev_data['day'] > test_day].copy()

    forecasts = []
    for _, row in future_days_data.iterrows():
        day_num = row['day']
        hist_values = []

        for hist_year in HISTORICAL_YEARS:
            hist_col = f'y{hist_year}'
            val = rev_data.loc[rev_data['day'] == day_num, hist_col].iloc[0]
            if val > 0.01:
                hist_values.append(val)

        if len(hist_values) > 0:
            forecasts.append(np.mean(hist_values))
        else:
            forecasts.append(np.nan)

    forecast = np.array(forecasts)
    return forecast, f"N years: {len(HISTORICAL_YEARS)}"


def exponential_smoothing_forecast(df, rev_type, test_day):
    """Simple exponential smoothing on year-to-date data"""
    rev_data = df[df['rev'] == rev_type].copy()

    # Get actual data up to test_day
    train_data = rev_data[rev_data['day'] <= test_day].copy()
    train_data = train_data[train_data[ACTUAL_YEAR_COL] > 0.01]

    if len(train_data) < 10:
        return None

    # Calculate daily changes
    values = train_data[ACTUAL_YEAR_COL].values
    daily_changes = np.diff(values)

    # Simple exponential smoothing on changes
    alpha = 0.3  # Smoothing parameter
    smoothed_change = daily_changes[0]
    for change in daily_changes[1:]:
        smoothed_change = alpha * change + (1 - alpha) * smoothed_change

    # Forecast by applying smoothed change
    last_value = values[-1]
    num_future_days = len(rev_data[rev_data['day'] > test_day])

    forecast = []
    current_val = last_value
    for _ in range(num_future_days):
        current_val += smoothed_change
        forecast.append(current_val)

    return np.array(forecast), f"α: {alpha}"


def ensemble_forecast(forecasts_dict):
    """Average of all available forecasts"""
    valid_forecasts = [f for f in forecasts_dict.values() if f is not None]

    if len(valid_forecasts) == 0:
        return None

    # Average forecasts
    ensemble = np.mean(valid_forecasts, axis=0)
    return ensemble, f"N models: {len(valid_forecasts)}"


# Try to import Prophet
try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
    print("✓ Prophet available - will include in comparison")
except ImportError:
    PROPHET_AVAILABLE = False
    print("⚠ Prophet not installed - run: python -m pip install prophet")
    print("  (Continuing with other methods...)")

if SKLEARN_AVAILABLE:
    print("✓ scikit-learn available - Linear Trend will be included")
else:
    print("⚠ scikit-learn not available - Linear Trend will be skipped")

print()

def prophet_forecast(df, rev_type, test_day):
    """Facebook Prophet forecast"""
    if not PROPHET_AVAILABLE:
        return None

    rev_data = df[df['rev'] == rev_type].copy()

    # Prepare data for Prophet
    train_data = rev_data[rev_data['day'] <= test_day].copy()
    train_data = train_data[train_data[ACTUAL_YEAR_COL] > 0.01]

    if len(train_data) < 30:
        return None

    prophet_df = pd.DataFrame({
        'ds': train_data['date'],
        'y': train_data[ACTUAL_YEAR_COL]
    })

    # Fit Prophet model
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False,
        seasonality_mode='multiplicative'
    )

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model.fit(prophet_df)

    # Forecast future
    future_dates = rev_data[rev_data['day'] > test_day]['date']
    future_df = pd.DataFrame({'ds': future_dates})
    forecast_df = model.predict(future_df)

    return forecast_df['yhat'].values, "Bayesian"


# ============================================================================
# RUN COMPARISON
# ============================================================================

print("Running forecast comparisons...")
print()

results = {}

for rev_type in REVENUE_TYPES:
    print(f"\n{'='*70}")
    print(f"Analyzing: {rev_type}")
    print(f"{'='*70}")

    rev_data = df[df['rev'] == rev_type].copy()

    # Get actual values for comparison
    actual_future = rev_data[rev_data['day'] > FORECAST_FROM_DAY][ACTUAL_YEAR_COL].values
    future_dates = rev_data[rev_data['day'] > FORECAST_FROM_DAY]['date'].values

    if len(actual_future) == 0:
        print(f"⚠ Not enough future data to test")
        continue

    # Run each forecast method
    forecasts = {}
    metadata = {}

    print("\nForecast Methods:")
    print("-" * 70)

    # Method 1: Growth-Adjusted Prior Year
    result = growth_adjusted_forecast(df, rev_type, FORECAST_FROM_DAY)
    if result is not None:
        forecasts['Growth-Adjusted'], metadata['Growth-Adjusted'] = result
        print(f"✓ Growth-Adjusted Prior Year: {metadata['Growth-Adjusted']}")

    # Method 2: Linear Trend
    result = linear_trend_forecast(df, rev_type, FORECAST_FROM_DAY)
    if result is not None:
        forecasts['Linear Trend'], metadata['Linear Trend'] = result
        print(f"✓ Linear Trend: {metadata['Linear Trend']}")

    # Method 3: Historical Average
    result = historical_average_forecast(df, rev_type, FORECAST_FROM_DAY)
    if result is not None:
        forecasts['Historical Avg'], metadata['Historical Avg'] = result
        print(f"✓ Historical Average: {metadata['Historical Avg']}")

    # Method 4: Exponential Smoothing
    result = exponential_smoothing_forecast(df, rev_type, FORECAST_FROM_DAY)
    if result is not None:
        forecasts['Exp Smoothing'], metadata['Exp Smoothing'] = result
        print(f"✓ Exponential Smoothing: {metadata['Exp Smoothing']}")

    # Method 5: Prophet
    if PROPHET_AVAILABLE:
        result = prophet_forecast(df, rev_type, FORECAST_FROM_DAY)
        if result is not None:
            forecasts['Prophet'], metadata['Prophet'] = result
            print(f"✓ Prophet (Bayesian): {metadata['Prophet']}")

    # Method 6: Ensemble
    ensemble_result = ensemble_forecast(forecasts)
    if ensemble_result is not None:
        forecasts['Ensemble'], metadata['Ensemble'] = ensemble_result
        print(f"✓ Ensemble: {metadata['Ensemble']}")

    # Calculate accuracy metrics
    print("\n\nAccuracy Metrics (vs Actual 2024 data):")
    print("-" * 70)
    print(f"{'Method':<25} {'MAE':>12} {'MAPE':>12} {'Final Error':>15}")
    print("-" * 70)

    accuracy_results = []

    for method_name, forecast in forecasts.items():
        # Mean Absolute Error
        mae = np.mean(np.abs(forecast - actual_future))

        # Mean Absolute Percentage Error
        mape = np.mean(np.abs((actual_future - forecast) / actual_future)) * 100

        # Final value error
        final_error = (forecast[-1] - actual_future[-1]) / actual_future[-1] * 100

        accuracy_results.append({
            'method': method_name,
            'mae': mae,
            'mape': mape,
            'final_error': final_error
        })

        print(f"{method_name:<25} ${mae:>10,.2f}M {mape:>10.2f}% {final_error:>+13.2f}%")

    # Store results
    results[rev_type] = {
        'forecasts': forecasts,
        'actual': actual_future,
        'dates': future_dates,
        'accuracy': accuracy_results,
        'metadata': metadata
    }

    # Find best method
    best_method = min(accuracy_results, key=lambda x: x['mape'])
    print("-" * 70)
    print(f"🏆 Most Accurate: {best_method['method']} (MAPE: {best_method['mape']:.2f}%)")


# ============================================================================
# CREATE VISUALIZATIONS
# ============================================================================

print("\n\n" + "="*70)
print("Creating visualizations...")
print("="*70)

for rev_type in REVENUE_TYPES:
    if rev_type not in results:
        continue

    result_data = results[rev_type]

    # Create subplot
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=(
            f'{rev_type} - Forecast Comparison',
            'Forecast Errors'
        ),
        vertical_spacing=0.15,
        row_heights=[0.7, 0.3]
    )

    # Get full year actual data for context
    rev_data = df[df['rev'] == rev_type].copy()
    historical_data = rev_data[rev_data['day'] <= FORECAST_FROM_DAY]

    # Plot historical actual
    fig.add_trace(
        go.Scatter(
            x=historical_data['date'],
            y=historical_data[ACTUAL_YEAR_COL],
            name='Actual (Historical)',
            mode='lines',
            line=dict(color='black', width=3)
        ),
        row=1, col=1
    )

    # Plot actual future (what we're trying to predict)
    fig.add_trace(
        go.Scatter(
            x=result_data['dates'],
            y=result_data['actual'],
            name='Actual (True Values)',
            mode='lines',
            line=dict(color='red', width=3, dash='solid')
        ),
        row=1, col=1
    )

    # Plot each forecast
    colors = ['blue', 'green', 'orange', 'purple', 'brown', 'pink']

    for idx, (method_name, forecast) in enumerate(result_data['forecasts'].items()):
        color = colors[idx % len(colors)]

        fig.add_trace(
            go.Scatter(
                x=result_data['dates'],
                y=forecast,
                name=method_name,
                mode='lines',
                line=dict(color=color, width=2, dash='dash')
            ),
            row=1, col=1
        )

        # Plot errors
        errors = forecast - result_data['actual']
        fig.add_trace(
            go.Scatter(
                x=result_data['dates'],
                y=errors,
                name=f'{method_name} Error',
                mode='lines',
                line=dict(color=color, width=1),
                showlegend=False
            ),
            row=2, col=1
        )

    # Add zero line to error plot
    fig.add_hline(y=0, line_dash="dash", line_color="black", row=2, col=1)

    # Update layout
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Revenue ($M)", row=1, col=1)
    fig.update_yaxes(title_text="Forecast Error ($M)", row=2, col=1)

    fig.update_layout(
        height=800,
        title_text=f"Forecast Model Comparison: {rev_type}<br><sub>Forecast starts at day {FORECAST_FROM_DAY} (Jan 2024)</sub>",
        hovermode='x unified',
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.99
        )
    )

    # Save plot
    filename = f'forecast_comparison_{rev_type.replace(" ", "_").replace("/", "_")}.html'
    fig.write_html(filename)
    print(f"✓ Saved: {filename}")

# ============================================================================
# SUMMARY REPORT
# ============================================================================

print("\n\n" + "="*70)
print("SUMMARY & RECOMMENDATIONS")
print("="*70)

print("\nOverall Performance by Method:")
print("-" * 70)

# Aggregate results across all revenue types
method_performance = {}

for rev_type, result_data in results.items():
    for acc in result_data['accuracy']:
        method = acc['method']
        if method not in method_performance:
            method_performance[method] = {'mape': [], 'mae': [], 'final_error': []}

        method_performance[method]['mape'].append(acc['mape'])
        method_performance[method]['mae'].append(acc['mae'])
        method_performance[method]['final_error'].append(abs(acc['final_error']))

print(f"{'Method':<25} {'Avg MAPE':>12} {'Avg MAE':>12} {'Avg Final Error':>15}")
print("-" * 70)

summary_results = []
for method, metrics in method_performance.items():
    avg_mape = np.mean(metrics['mape'])
    avg_mae = np.mean(metrics['mae'])
    avg_final = np.mean(metrics['final_error'])

    summary_results.append({
        'method': method,
        'avg_mape': avg_mape,
        'avg_mae': avg_mae,
        'avg_final': avg_final
    })

    print(f"{method:<25} {avg_mape:>11.2f}% ${avg_mae:>10,.2f}M {avg_final:>13.2f}%")

print("-" * 70)

# Find best overall method
best_overall = min(summary_results, key=lambda x: x['avg_mape'])
print(f"\n🏆 BEST OVERALL METHOD: {best_overall['method']}")
print(f"   Average MAPE: {best_overall['avg_mape']:.2f}%")

print("\n\nRecommendations:")
print("-" * 70)

# Provide recommendations based on results
if PROPHET_AVAILABLE:
    prophet_result = next((r for r in summary_results if r['method'] == 'Prophet'), None)
    if prophet_result and prophet_result['avg_mape'] < 5:
        print("✓ Prophet performs well and provides uncertainty intervals")
        print("  → RECOMMEND adding to dashboard")
    else:
        print("⚠ Prophet available but not significantly better than simpler methods")

ensemble_result = next((r for r in summary_results if r['method'] == 'Ensemble'), None)
if ensemble_result:
    print(f"\n✓ Ensemble achieves {ensemble_result['avg_mape']:.2f}% MAPE")
    print("  → Combining methods reduces risk of any single model being wrong")
    print("  → RECOMMEND for conservative forecasting")

current_result = next((r for r in summary_results if r['method'] == 'Growth-Adjusted'), None)
if current_result:
    print(f"\n✓ Current method (Growth-Adjusted) achieves {current_result['avg_mape']:.2f}% MAPE")
    if current_result == best_overall:
        print("  → Already using the best method!")
    else:
        improvement = current_result['avg_mape'] - best_overall['avg_mape']
        print(f"  → Could improve by {improvement:.2f}% with {best_overall['method']}")

print("\n\nNext Steps:")
print("-" * 70)
print("1. Review the HTML visualization files created in this directory")
print("2. Consider which methods best fit your forecasting needs")
print("3. Decide if you want to add Prophet, Ensemble, or other methods")
print("\n" + "="*70)
print("Analysis complete!")
print("="*70)
