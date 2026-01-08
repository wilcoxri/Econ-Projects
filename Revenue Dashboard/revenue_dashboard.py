import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Revenue Collections Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Utah GOPB Color Scheme
COLORS = {
    'primary': '#112347',        # Dark navy blue
    'primary_dark': '#0a1429',
    'primary_light': '#e6edfb',
    'secondary': '#be3c3f',      # Burgundy red
    'secondary_dark': '#832123',
    'secondary_light': '#fdd2d2',
    'accent': '#f6c13e',         # Golden yellow
    'accent_dark': '#d39b0f',
    'accent_light': '#fdf1d4',
    'gray': '#474747',
    'white': '#ffffff',
    'black': '#000000'
}

# Custom CSS for Utah GOPB styling
st.markdown(f"""
<style>
    /* Header styling */
    .stApp header {{
        background-color: {COLORS['primary']};
    }}

    /* Main title */
    h1 {{
        color: {COLORS['primary']} !important;
    }}

    /* Section headers */
    h2, h3 {{
        color: {COLORS['primary']} !important;
    }}

    /* Metric labels */
    [data-testid="stMetricLabel"] {{
        color: {COLORS['gray']} !important;
    }}

    /* Metric values */
    [data-testid="stMetricValue"] {{
        color: {COLORS['primary']} !important;
    }}

    /* Buttons and interactive elements */
    .stButton > button {{
        background-color: {COLORS['accent']};
        color: {COLORS['primary']};
        border: none;
    }}

    .stButton > button:hover {{
        background-color: {COLORS['accent_dark']};
        color: {COLORS['white']};
    }}

    /* Selectbox styling */
    .stSelectbox > div > div {{
        border-color: {COLORS['primary']};
    }}

    /* Expander header */
    .streamlit-expanderHeader {{
        color: {COLORS['primary']} !important;
    }}

    /* Links */
    a {{
        color: {COLORS['secondary']} !important;
    }}

    /* Divider lines */
    hr {{
        border-color: {COLORS['primary_light']};
    }}
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("Revenue Collections Dashboard")
st.markdown("---")

# Load official forecast data
@st.cache_data
def load_official_forecast():
    """Load the official state forecast from FY26 forecast.csv"""
    try:
        forecast_df = pd.read_csv('FY26 forecast.csv')
        # Clean up column names
        forecast_df.columns = forecast_df.columns.str.strip()
        # Clean up revenue names
        forecast_df['Rev'] = forecast_df['Rev'].str.strip()

        # Parse Level Forecast (remove commas and convert to float)
        forecast_df['Level Forecast'] = forecast_df['Level Forecast'].str.replace(',', '').str.strip()
        forecast_df['Level Forecast'] = pd.to_numeric(forecast_df['Level Forecast'], errors='coerce')

        # Parse Growth Forecast (remove % and convert to float)
        forecast_df['Growth Forecast'] = forecast_df['Growth Forecast'].str.replace('%', '').str.strip()
        forecast_df['Growth Forecast'] = pd.to_numeric(forecast_df['Growth Forecast'], errors='coerce')

        # Create dictionaries for easy lookup
        level_forecast = dict(zip(forecast_df['Rev'], forecast_df['Level Forecast']))
        growth_forecast = dict(zip(forecast_df['Rev'], forecast_df['Growth Forecast']))

        return level_forecast, growth_forecast
    except FileNotFoundError:
        return {}, {}

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('rev9.csv', thousands=',')

    # Parse date column
    df['date'] = pd.to_datetime(df['date'], format='%d%b%Y')

    # Get year columns
    year_cols = [col for col in df.columns if col.startswith('y')]

    # Convert year columns to numeric, handling commas and replacing any non-numeric values with NaN
    for col in year_cols:
        # If column is object type (string), remove commas first
        if df[col].dtype == 'object':
            df[col] = df[col].str.replace(',', '')
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Fill NaN values with 0
    df[year_cols] = df[year_cols].fillna(0)

    # Create Individual Income Tax category by combining Withholding, Gross Payments, and Refunds
    income_tax_components = ['Withholding', 'Gross Payments', 'Refunds']

    # Filter for the three component categories
    component_data = df[df['rev'].isin(income_tax_components)].copy()

    if len(component_data) > 0:
        # Group by day/date and sum the year columns
        income_tax_data = component_data.groupby(['day', 'date']).agg({
            **{col: 'sum' for col in year_cols}
        }).reset_index()

        # Add the revenue type column
        income_tax_data['rev'] = 'Individual Income Tax'

        # Reorder columns to match original dataframe
        income_tax_data = income_tax_data[['rev', 'day', 'date'] + year_cols]

        # Append to the main dataframe
        df = pd.concat([df, income_tax_data], ignore_index=True)

    # Create Final Payments category by combining Gross Payments and Refunds
    final_payments_components = ['Gross Payments', 'Refunds']

    # Filter for the component categories
    final_payments_component_data = df[df['rev'].isin(final_payments_components)].copy()

    if len(final_payments_component_data) > 0:
        # Group by day/date and sum the year columns
        final_payments_data = final_payments_component_data.groupby(['day', 'date']).agg({
            **{col: 'sum' for col in year_cols}
        }).reset_index()

        # Add the revenue type column
        final_payments_data['rev'] = 'Final Payments'

        # Reorder columns to match original dataframe
        final_payments_data = final_payments_data[['rev', 'day', 'date'] + year_cols]

        # Append to the main dataframe
        df = pd.concat([df, final_payments_data], ignore_index=True)

    # Create Sales and Use Tax (GF) category with year-specific percentages
    sales_tax_data = df[df['rev'] == 'Sales and Use Tax'].copy()

    if len(sales_tax_data) > 0:
        # Define the percentage allocations for each year
        gf_percentages = {
            'y2026': 0.66098,
            'y2025': 0.72963,
            'y2024': 0.73003,
            'y2023': 0.7312089,
            'y2022': 0.740058
        }

        # Apply the percentages to each year column
        for year_col, percentage in gf_percentages.items():
            if year_col in sales_tax_data.columns:
                sales_tax_data[year_col] = sales_tax_data[year_col] * percentage

        # Update the revenue type
        sales_tax_data['rev'] = 'Sales and Use Tax (GF)'

        # Append to the main dataframe
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

    # Filter for the component categories
    gf_component_data = df[df['rev'].isin(general_fund_components)].copy()

    if len(gf_component_data) > 0:
        # Group by day/date and sum the year columns
        general_fund_data = gf_component_data.groupby(['day', 'date']).agg({
            **{col: 'sum' for col in year_cols}
        }).reset_index()

        # Add the revenue type column
        general_fund_data['rev'] = 'General Fund'

        # Reorder columns to match original dataframe
        general_fund_data = general_fund_data[['rev', 'day', 'date'] + year_cols]

        # Append to the main dataframe
        df = pd.concat([df, general_fund_data], ignore_index=True)

    # Create Income Tax Fund category by combining multiple revenue sources
    income_tax_fund_components = [
        'Individual Income Tax',
        'Corporate Tax & Gross Receipts',
        'Mineral Production Withholding',
        'Income Tax Fund Other'
    ]

    # Filter for the component categories
    itf_component_data = df[df['rev'].isin(income_tax_fund_components)].copy()

    if len(itf_component_data) > 0:
        # Group by day/date and sum the year columns
        income_tax_fund_data = itf_component_data.groupby(['day', 'date']).agg({
            **{col: 'sum' for col in year_cols}
        }).reset_index()

        # Add the revenue type column
        income_tax_fund_data['rev'] = 'Income Tax Fund'

        # Reorder columns to match original dataframe
        income_tax_fund_data = income_tax_fund_data[['rev', 'day', 'date'] + year_cols]

        # Append to the main dataframe
        df = pd.concat([df, income_tax_fund_data], ignore_index=True)

    # Create GF/ITF category by combining General Fund and Income Tax Fund
    gf_itf_components = ['General Fund', 'Income Tax Fund']

    # Filter for the component categories
    gf_itf_component_data = df[df['rev'].isin(gf_itf_components)].copy()

    if len(gf_itf_component_data) > 0:
        # Group by day/date and sum the year columns
        gf_itf_data = gf_itf_component_data.groupby(['day', 'date']).agg({
            **{col: 'sum' for col in year_cols}
        }).reset_index()

        # Add the revenue type column
        gf_itf_data['rev'] = 'GF/ITF'

        # Reorder columns to match original dataframe
        gf_itf_data = gf_itf_data[['rev', 'day', 'date'] + year_cols]

        # Append to the main dataframe
        df = pd.concat([df, gf_itf_data], ignore_index=True)

    return df, year_cols

# Forecast generation function
def generate_forecast(df, rev_type, forecast_year, method, historical_years, confidence_level=80):
    """
    Generate proportion-based forecast for a revenue type and year.

    Uses historical proportions to estimate year-end total based on current YTD.
    """
    # Get data for this revenue type
    rev_data = df[df['rev'] == rev_type].copy()

    year_col = f'y{forecast_year}'
    forecast_year_int = int(forecast_year)
    prior_year = str(forecast_year_int - 1)
    prior_year_col = f'y{prior_year}'

    # Find where current year data ends (last non-zero value)
    non_zero_mask = rev_data[year_col].abs() > 0.01
    if not non_zero_mask.any():
        return None, None, None, None, None

    last_actual_idx = rev_data[non_zero_mask].index[-1]
    last_actual_day = rev_data.loc[last_actual_idx, 'day']
    last_actual_value = rev_data.loc[last_actual_idx, year_col]

    # Get future days for the forecast line
    future_data = rev_data[rev_data['day'] > last_actual_day].copy()

    if len(future_data) == 0:
        return None, None, None, None, None

    # Calculate historical proportions collected by this day
    proportions = []
    for year in historical_years:
        col = f'y{year}'
        if col in rev_data.columns:
            ytd_value = rev_data.loc[rev_data['day'] == last_actual_day, col]
            if len(ytd_value) > 0:
                ytd_val = ytd_value.iloc[0]
                # For negative values (like refunds), use min; otherwise use max
                if rev_data[col].mean() < 0:
                    total_value = rev_data[col].min()
                else:
                    total_value = rev_data[col].max()
                if abs(total_value) > 0.01:
                    prop = ytd_val / total_value
                    proportions.append(prop)

    if len(proportions) == 0:
        return None, None, None, None, None

    avg_proportion = np.mean(proportions)
    proportion_std = np.std(proportions) if len(proportions) > 1 else 0.02

    # Calculate forecasted year-end total
    forecast_total = last_actual_value / avg_proportion

    # Calculate implied growth rate
    if prior_year_col in rev_data.columns:
        if rev_data[prior_year_col].mean() < 0:
            prior_year_total = rev_data[prior_year_col].min()
        else:
            prior_year_total = rev_data[prior_year_col].max()
        implied_growth = (forecast_total - prior_year_total) / abs(prior_year_total) if abs(prior_year_total) > 0.01 else 0
    else:
        prior_year_total = None
        implied_growth = None

    # Calculate confidence intervals based on proportion variability
    from scipy import stats
    z_score = stats.norm.ppf((1 + confidence_level/100) / 2)

    # Confidence bounds on the total
    lower_total = last_actual_value / (avg_proportion + z_score * proportion_std)
    upper_total = last_actual_value / (avg_proportion - z_score * proportion_std)

    # Ensure bounds are in correct order (can flip for negative values)
    if lower_total > upper_total:
        lower_total, upper_total = upper_total, lower_total

    # Create forecast line that approaches the forecasted total
    # Use prior year's pattern scaled to reach the forecast total
    if prior_year_col in rev_data.columns:
        prior_year_future = rev_data.loc[rev_data['day'] > last_actual_day, prior_year_col].values
        prior_year_ytd = rev_data.loc[rev_data['day'] == last_actual_day, prior_year_col].iloc[0]

        if abs(prior_year_ytd) > 0.01:
            # Scale prior year pattern to match current level and reach forecast total
            scale_factor = forecast_total / prior_year_total if abs(prior_year_total) > 0.01 else 1.0
            future_data['forecast'] = prior_year_future * scale_factor

            lower_scale = lower_total / prior_year_total if abs(prior_year_total) > 0.01 else scale_factor * 0.95
            upper_scale = upper_total / prior_year_total if abs(prior_year_total) > 0.01 else scale_factor * 1.05

            future_data['lower_bound'] = prior_year_future * lower_scale
            future_data['upper_bound'] = prior_year_future * upper_scale
        else:
            # Fallback: linear interpolation to forecast total
            remaining_days = len(future_data)
            remaining_amount = forecast_total - last_actual_value
            daily_increment = remaining_amount / remaining_days

            forecast_vals = [last_actual_value + daily_increment * (i + 1) for i in range(remaining_days)]
            future_data['forecast'] = forecast_vals

            lower_remaining = lower_total - last_actual_value
            upper_remaining = upper_total - last_actual_value
            future_data['lower_bound'] = [last_actual_value + (lower_remaining / remaining_days) * (i + 1) for i in range(remaining_days)]
            future_data['upper_bound'] = [last_actual_value + (upper_remaining / remaining_days) * (i + 1) for i in range(remaining_days)]
    else:
        return None, None, None, None, None

    # Remove NaN forecasts
    future_data = future_data.dropna(subset=['forecast'])

    if len(future_data) == 0:
        return None, None, None, None, None

    # Return implied growth rate as percentage
    growth_rate_pct = implied_growth * 100 if implied_growth is not None else None

    return (future_data['date'].values,
            future_data['forecast'].values,
            growth_rate_pct,
            future_data['lower_bound'].values,
            future_data['upper_bound'].values)

def calculate_probability_method1(df, rev_type, consensus_total):
    """Method 1: Model Forecast Distribution"""
    rev_data = df[df['rev'] == rev_type].copy()
    year_col = 'y2026'
    prior_year_col = 'y2025'

    non_zero_mask = rev_data[year_col].abs() > 0.01
    if not non_zero_mask.any():
        return None

    last_actual_idx = rev_data[non_zero_mask].index[-1]
    last_actual_day = rev_data.loc[last_actual_idx, 'day']
    last_actual_value = rev_data.loc[last_actual_idx, year_col]

    prior_value = rev_data.loc[rev_data['day'] == last_actual_day, prior_year_col].iloc[0]
    if abs(prior_value) < 0.01:
        return None

    growth_rate = (last_actual_value - prior_value) / prior_value

    # Historical growth rate volatility
    historical_years = ['2022', '2023', '2024', '2025']
    historical_growth_rates = []

    for i in range(len(historical_years) - 1):
        y1, y2 = historical_years[i], historical_years[i + 1]
        col1, col2 = f'y{y1}', f'y{y2}'

        if col1 in rev_data.columns and col2 in rev_data.columns:
            val1 = rev_data.loc[rev_data['day'] == last_actual_day, col1]
            val2 = rev_data.loc[rev_data['day'] == last_actual_day, col2]

            if len(val1) > 0 and len(val2) > 0:
                v1, v2 = val1.iloc[0], val2.iloc[0]
                if abs(v1) > 0.01:
                    historical_growth_rates.append((v2 - v1) / v1)

    growth_std = np.std(historical_growth_rates) if len(historical_growth_rates) > 1 else 0.05

    # For negative values (like refunds), use min instead of max to get the "total"
    if rev_data[prior_year_col].mean() < 0:
        prior_year_total = rev_data[prior_year_col].min()
    else:
        prior_year_total = rev_data[prior_year_col].max()
    prior_year_remaining = prior_year_total - prior_value
    forecast_total = last_actual_value + (prior_year_remaining * (1 + growth_rate))
    forecast_std = prior_year_remaining * growth_std

    if forecast_std <= 0:
        return None

    from scipy import stats
    z_score = (consensus_total - forecast_total) / forecast_std
    probability = (1 - stats.norm.cdf(z_score)) * 100

    return probability


def calculate_probability_method2(df, rev_type, consensus_growth):
    """Method 2: Growth Rate Distribution"""
    rev_data = df[df['rev'] == rev_type].copy()
    year_col = 'y2026'
    prior_year_col = 'y2025'

    non_zero_mask = rev_data[year_col].abs() > 0.01
    if not non_zero_mask.any():
        return None

    last_actual_idx = rev_data[non_zero_mask].index[-1]
    last_actual_day = rev_data.loc[last_actual_idx, 'day']
    last_actual_value = rev_data.loc[last_actual_idx, year_col]

    prior_value = rev_data.loc[rev_data['day'] == last_actual_day, prior_year_col].iloc[0]
    if abs(prior_value) < 0.01:
        return None

    current_growth = (last_actual_value - prior_value) / prior_value * 100

    # Historical growth rate volatility
    historical_years = ['2022', '2023', '2024', '2025']
    historical_growth_rates = []

    for i in range(len(historical_years) - 1):
        y1, y2 = historical_years[i], historical_years[i + 1]
        col1, col2 = f'y{y1}', f'y{y2}'

        if col1 in rev_data.columns and col2 in rev_data.columns:
            # For negative values (like refunds), use min instead of max
            if rev_data[col1].mean() < 0:
                total1 = rev_data[col1].min()
                total2 = rev_data[col2].min()
            else:
                total1 = rev_data[col1].max()
                total2 = rev_data[col2].max()
            if abs(total1) > 0.01:
                historical_growth_rates.append((total2 - total1) / total1 * 100)

    growth_std = np.std(historical_growth_rates) if len(historical_growth_rates) > 1 else 5.0

    # Adjust for time remaining
    total_days = 365
    days_remaining = total_days - last_actual_day
    time_factor = np.sqrt(days_remaining / total_days)
    adjusted_std = growth_std * time_factor

    if adjusted_std <= 0:
        return None

    from scipy import stats
    z_score = (consensus_growth - current_growth) / adjusted_std
    probability = (1 - stats.norm.cdf(z_score)) * 100

    return probability


def calculate_probability_method3(df, rev_type, consensus_total, n_simulations=10000):
    """Method 3: Monte Carlo Simulation"""
    rev_data = df[df['rev'] == rev_type].copy()
    year_col = 'y2026'
    prior_year_col = 'y2025'

    non_zero_mask = rev_data[year_col].abs() > 0.01
    if not non_zero_mask.any():
        return None

    last_actual_idx = rev_data[non_zero_mask].index[-1]
    last_actual_day = rev_data.loc[last_actual_idx, 'day']
    last_actual_value = rev_data.loc[last_actual_idx, year_col]

    prior_value = rev_data.loc[rev_data['day'] == last_actual_day, prior_year_col].iloc[0]
    # For negative values (like refunds), use min instead of max
    if rev_data[prior_year_col].mean() < 0:
        prior_year_total = rev_data[prior_year_col].min()
    else:
        prior_year_total = rev_data[prior_year_col].max()

    if abs(prior_value) < 0.01:
        return None

    current_growth = (last_actual_value - prior_value) / prior_value

    # Historical growth rate volatility
    historical_years = ['2022', '2023', '2024', '2025']
    historical_growth_rates = []

    for i in range(len(historical_years) - 1):
        y1, y2 = historical_years[i], historical_years[i + 1]
        col1, col2 = f'y{y1}', f'y{y2}'

        if col1 in rev_data.columns and col2 in rev_data.columns:
            # For negative values (like refunds), use min instead of max
            if rev_data[col1].mean() < 0:
                total1 = rev_data[col1].min()
                total2 = rev_data[col2].min()
            else:
                total1 = rev_data[col1].max()
                total2 = rev_data[col2].max()
            if abs(total1) > 0.01:
                historical_growth_rates.append((total2 - total1) / total1)

    growth_std = np.std(historical_growth_rates) if len(historical_growth_rates) > 1 else 0.05

    prior_year_remaining = prior_year_total - prior_value
    days_remaining = 365 - last_actual_day
    time_factor = np.sqrt(days_remaining / 365)
    adjusted_std = growth_std * time_factor

    simulated_totals = []
    for _ in range(n_simulations):
        simulated_growth = np.random.normal(current_growth, adjusted_std)
        simulated_total = last_actual_value + (prior_year_remaining * (1 + simulated_growth))
        simulated_totals.append(simulated_total)

    probability = np.mean(np.array(simulated_totals) >= consensus_total) * 100
    return probability


def calculate_average_probability(df, rev_type, consensus_total, consensus_growth):
    """Calculate average probability across three methods with confidence bounds"""
    if consensus_total is None or consensus_growth is None:
        return None, None, None

    prob1 = calculate_probability_method1(df, rev_type, consensus_total)
    prob2 = calculate_probability_method2(df, rev_type, consensus_growth)
    prob3 = calculate_probability_method3(df, rev_type, consensus_total)

    valid_probs = [p for p in [prob1, prob2, prob3] if p is not None]
    if len(valid_probs) > 0:
        avg_prob = np.mean(valid_probs)
        min_prob = np.min(valid_probs)
        max_prob = np.max(valid_probs)
        return avg_prob, min_prob, max_prob
    return None, None, None


def create_probability_needle(probability, fund_name, prob_min=None, prob_max=None):
    """Create NYT-style needle gauge for probability with optional confidence band"""
    if probability is None:
        return None

    # Determine color based on probability ranges
    if probability >= 70:
        color = "#2ecc71"  # Green - high probability
    elif probability >= 50:
        color = "#f39c12"  # Orange - medium probability
    else:
        color = "#e74c3c"  # Red - low probability

    # Build gauge steps - background zones plus confidence band
    gauge_steps = [
        {'range': [0, 50], 'color': '#ffebee'},    # Light red
        {'range': [50, 70], 'color': '#fff8e1'},   # Light yellow
        {'range': [70, 100], 'color': '#e8f5e9'}   # Light green
    ]

    # Add confidence band as a highlighted arc if bounds are available
    if prob_min is not None and prob_max is not None and prob_min != prob_max:
        # Add confidence band overlay with semi-transparent color
        gauge_steps.append({
            'range': [prob_min, prob_max],
            'color': 'rgba(17, 35, 71, 0.25)'  # Semi-transparent navy
        })

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=probability,
        domain={'x': [0, 1], 'y': [0, 1]},
        number={
            'suffix': "%",
            'font': {'size': 40, 'color': color}
        },
        gauge={
            'axis': {
                'range': [0, 100],
                'tickwidth': 1,
                'tickcolor': "darkgray",
                'tickmode': 'linear',
                'tick0': 0,
                'dtick': 20
            },
            'bar': {'color': color, 'thickness': 0.3},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "lightgray",
            'steps': gauge_steps,
            'threshold': {
                'line': {'color': color, 'width': 4},
                'thickness': 0.75,
                'value': probability
            }
        }
    ))

    # Build title without range (range will be shown as annotation above the number)
    title_text = f"{fund_name}<br><span style='font-size:12px;color:#666;font-weight:normal'>Probability of Reaching Forecast</span>"

    fig.update_layout(
        height=260,
        margin=dict(l=20, r=20, t=60, b=10),
        paper_bgcolor="white",
        font={'color': "darkgray", 'family': "Arial"},
        title={
            'text': title_text,
            'y': 0.92,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 18, 'color': COLORS['primary'], 'family': 'Arial Black'}
        }
    )

    # Add range annotation directly above the point estimate
    if prob_min is not None and prob_max is not None:
        fig.add_annotation(
            text=f"Range: {prob_min:.0f}% - {prob_max:.0f}%",
            x=0.5,
            y=0.35,
            xref="paper",
            yref="paper",
            showarrow=False,
            font=dict(size=11, color="#888"),
            xanchor="center",
            yanchor="bottom"
        )

    return fig


def generate_official_forecast_line(df, rev_type, official_total):
    """
    Generate official forecast line as a horizontal line at the forecast total.

    Parameters:
    - df: Full dataframe
    - rev_type: Revenue category
    - official_total: Official forecasted total for FY26

    Returns:
    - Tuple of (dates, forecast_values) or (None, None)
    """
    rev_data = df[df['rev'] == rev_type].copy()

    if len(rev_data) == 0:
        return None, None

    # Get all dates for the fiscal year to draw the line across entire chart
    all_dates = rev_data['date'].values

    # Create horizontal line at the official forecast total
    forecast_values = np.full(len(all_dates), official_total)

    return all_dates, forecast_values

try:
    df, year_cols = load_data()
    official_level_forecast, official_growth_forecast = load_official_forecast()

    # Set default years for comparison (all available years)
    available_years = [col.replace('y', '') for col in year_cols]
    selected_years = ['2022', '2023', '2024', '2025', '2026']

    # Set default forecast year to current fiscal year (2026)
    forecast_years = ['2026']

    # Key Metrics Section
    st.header("Key Metrics")

    # Function to get current growth rate for a revenue type
    def get_current_growth(rev_type):
        rev_type_data = df[df['rev'] == rev_type].copy()
        year_col = 'y2026'
        prior_year_col = 'y2025'

        if year_col in rev_type_data.columns and prior_year_col in rev_type_data.columns:
            latest_data = rev_type_data[
                (rev_type_data[year_col].abs() > 0.01) &
                (rev_type_data[prior_year_col].abs() > 0.01)
            ].copy()

            if len(latest_data) > 0:
                latest = latest_data.iloc[-1]
                current_val = latest[year_col]
                prior_val = latest[prior_year_col]
                return ((current_val - prior_val) / prior_val) * 100
        return None

    # Function to get 7-day moving average growth rate for a revenue type
    def get_7day_ma_growth(rev_type):
        rev_type_data = df[df['rev'] == rev_type].copy()
        year_col = 'y2026'
        prior_year_col = 'y2025'

        if year_col in rev_type_data.columns and prior_year_col in rev_type_data.columns:
            latest_data = rev_type_data[
                (rev_type_data[year_col].abs() > 0.01) &
                (rev_type_data[prior_year_col].abs() > 0.01)
            ].copy()

            if len(latest_data) > 0:
                # Calculate daily growth rates
                latest_data['growth_rate'] = ((latest_data[year_col] - latest_data[prior_year_col]) /
                                               latest_data[prior_year_col].abs() * 100)
                # Calculate 7-day moving average
                latest_data['growth_ma7'] = latest_data['growth_rate'].rolling(window=7, min_periods=1).mean()
                return latest_data['growth_ma7'].iloc[-1]
        return None

    # Display metrics for General Fund, Income Tax Fund, and GF/ITF
    funds = [
        ('General Fund', 'General Fund'),
        ('Income Tax Fund', 'Income Tax Fund'),
        ('GF/ITF', 'GF/ITF')
    ]

    # CSS for help tooltip (defined once outside the loop)
    st.markdown(f"""
    <style>
    .prob-help-container {{
        position: relative;
    }}
    .prob-help-icon {{
        position: absolute;
        top: 5px;
        right: 10px;
        cursor: help;
        color: {COLORS['gray']};
        font-size: 0.875rem;
        z-index: 1000;
        background: white;
        padding: 2px 5px;
        border-radius: 3px;
    }}
    .prob-help-tooltip {{
        display: none;
        position: absolute;
        background: white;
        border: 1px solid {COLORS['primary_light']};
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 8px rgba(17,35,71,0.15);
        z-index: 1001;
        width: 400px;
        right: 0px;
        top: 25px;
        font-size: 0.875rem;
        color: {COLORS['gray']};
    }}
    .prob-help-icon:hover .prob-help-tooltip {{
        display: block;
    }}
    </style>
    """, unsafe_allow_html=True)

    # Create three columns for the three funds side by side
    fund_cols = st.columns(3)

    for idx, (fund_name, fund_key) in enumerate(funds):
        with fund_cols[idx]:
            current_growth = get_current_growth(fund_key)
            growth_ma7 = get_7day_ma_growth(fund_key)
            consensus_growth = official_growth_forecast.get(fund_key, None)
            consensus_total = official_level_forecast.get(fund_key, None)

            # Calculate probability with confidence bounds
            probability, prob_min, prob_max = calculate_average_probability(df, fund_key, consensus_total, consensus_growth)

            # Show needle with metrics directly underneath
            if probability is not None:
                # Container with help icon overlay
                st.markdown("""
                <div class="prob-help-container">
                    <span class="prob-help-icon">
                        ?
                        <div class="prob-help-tooltip">
                            <strong>Probability Calculation Methodology:</strong><br><br>
                            The probability is calculated as an average of three independent methods:<br><br>
                            1. <strong>Model Forecast Distribution</strong>: Uses historical confidence intervals to estimate the probability based on where the consensus forecast falls within the expected range.<br><br>
                            2. <strong>Growth Rate Distribution</strong>: Analyzes historical volatility in growth rates and projects the likelihood of achieving the consensus growth rate.<br><br>
                            3. <strong>Monte Carlo Simulation</strong>: Runs 10,000 simulations using historical patterns to estimate the probability of reaching the consensus target.<br><br>
                            The final probability is the average of all three methods.
                        </div>
                    </span>
                </div>
                """, unsafe_allow_html=True)

                needle_fig = create_probability_needle(probability, fund_name, prob_min, prob_max)
                if needle_fig is not None:
                    st.plotly_chart(needle_fig, use_container_width=True)
            else:
                st.info("Probability calculation not available")

            # Metrics directly under the gauge - centered
            current_str = f"{current_growth:+.1f}%" if current_growth is not None else "N/A"
            ma7_str = f"{growth_ma7:+.1f}%" if growth_ma7 is not None else "N/A"
            consensus_str = f"{consensus_growth:+.1f}%" if consensus_growth is not None else "N/A"

            st.markdown(f"""
            <div style="text-align: center; margin-top: -10px;">
                <span style="font-size: 0.85rem; color: {COLORS['gray']};">Current YoY: </span>
                <span style="font-size: 1.1rem; font-weight: bold; color: {COLORS['primary']};">{current_str}</span>
                <span style="margin: 0 10px; color: {COLORS['primary_light']};">|</span>
                <span style="font-size: 0.85rem; color: {COLORS['gray']};">7-Day Avg: </span>
                <span style="font-size: 1.1rem; font-weight: bold; color: {COLORS['primary']};">{ma7_str}</span>
                <span style="margin: 0 10px; color: {COLORS['primary_light']};">|</span>
                <span style="font-size: 0.85rem; color: {COLORS['gray']};">Consensus: </span>
                <span style="font-size: 1.1rem; font-weight: bold; color: {COLORS['primary']};">{consensus_str}</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # Time Series Visualization
    st.header("Revenue Trends Over Time")

    # Revenue type filter and forecast options side by side
    col_filter, col_gap, col_forecast, col_spacer = st.columns([1, 0.3, 0.8, 2])
    with col_filter:
        all_revenue_types = sorted(df['rev'].unique())
        selected_revenue_type = st.selectbox(
            "Select Revenue Type",
            options=all_revenue_types,
            index=all_revenue_types.index("Sales and Use Tax (Total)") if "Sales and Use Tax (Total)" in all_revenue_types else 0
        )

    # Convert to list for compatibility with rest of code
    selected_revenue_types = [selected_revenue_type]

    # Filter data based on selections
    filtered_df = df[df['rev'].isin(selected_revenue_types)].copy()
    selected_year_cols = [f'y{year}' for year in selected_years]

    # Forecast options
    show_forecast = True  # Always show forecast
    forecast_method = "Proportion-Based"  # Default method

    with col_forecast:
        confidence_level = st.slider(
            "Forecast Confidence Interval",
            min_value=50,
            max_value=95,
            value=80,
            step=5,
            help="Width of confidence bands around forecast (higher = wider bands)"
        )

    # Create line chart
    fig_trends = go.Figure()

    for rev_type in selected_revenue_types:
        rev_data = filtered_df[filtered_df['rev'] == rev_type].copy()

        for year in selected_years:
            year_col = f'y{year}'
            if year_col in rev_data.columns:
                # Create a copy for this specific trace
                trace_data = rev_data[['date', year_col]].copy()

                # Find the last date with non-zero data
                # Use a small threshold to account for rounding (0.01M = $10,000)
                non_zero_mask = trace_data[year_col].abs() > 0.01

                if non_zero_mask.any():
                    last_data_idx = trace_data[non_zero_mask].index[-1]
                    # Only include data up to the last non-zero point
                    trace_data = trace_data.loc[:last_data_idx]

                fig_trends.add_trace(go.Scatter(
                    x=trace_data['date'],
                    y=trace_data[year_col],
                    name=year,
                    mode='lines',
                    hovertemplate='<b>%{fullData.name}</b><br>' +
                                  'Date: %{x|%b %d, %Y}<br>' +
                                  'Amount: $%{y:,.2f}M<br>' +
                                  '<extra></extra>'
                ))

    # Add forecast lines if enabled
    if show_forecast:
        # Determine historical years for forecasting (exclude forecast years)
        historical_years_for_forecast = [y for y in selected_years if y not in forecast_years]

        # Store growth rates for display
        growth_rates_info = []

        for rev_type in selected_revenue_types:
            for forecast_year in forecast_years:
                if forecast_year in selected_years:
                    # Generate forecast
                    forecast_dates, forecast_values, growth_rate_pct, lower_bound, upper_bound = generate_forecast(
                        df,
                        rev_type,
                        forecast_year,
                        forecast_method,
                        historical_years_for_forecast,
                        confidence_level
                    )

                    if forecast_dates is not None and forecast_values is not None:
                        # Add to growth rates info
                        if growth_rate_pct is not None:
                            growth_rates_info.append({
                                'Revenue Type': rev_type,
                                'Year': forecast_year,
                                'YoY Growth': f"{growth_rate_pct:+.2f}%"
                            })

                        # Add confidence band (shaded area)
                        if lower_bound is not None and upper_bound is not None:
                            fig_trends.add_trace(go.Scatter(
                                x=forecast_dates,
                                y=upper_bound,
                                mode='lines',
                                line=dict(width=0),
                                showlegend=False,
                                hoverinfo='skip'
                            ))

                            fig_trends.add_trace(go.Scatter(
                                x=forecast_dates,
                                y=lower_bound,
                                mode='lines',
                                line=dict(width=0),
                                fillcolor='rgba(68, 68, 68, 0.2)',
                                fill='tonexty',
                                name=f"{forecast_year} ({confidence_level}% CI)",
                                hovertemplate='<b>%{fullData.name}</b><br>' +
                                              'Date: %{x|%b %d, %Y}<br>' +
                                              'Lower: $%{y:,.2f}M<br>' +
                                              '<extra></extra>'
                            ))

                        # Add forecast line on top of confidence band
                        fig_trends.add_trace(go.Scatter(
                            x=forecast_dates,
                            y=forecast_values,
                            name=f"{forecast_year} (Forecast)",
                            mode='lines',
                            line=dict(dash='dash', width=2, color='black'),
                            opacity=0.9,
                            hovertemplate='<b>%{fullData.name}</b><br>' +
                                          'Date: %{x|%b %d, %Y}<br>' +
                                          'Forecast: $%{y:,.2f}M<br>' +
                                          '<extra></extra>'
                        ))

    # Add official state forecast line if available
    for rev_type in selected_revenue_types:
        if rev_type in official_level_forecast and official_level_forecast[rev_type] is not None:
            official_dates, official_values = generate_official_forecast_line(
                df, rev_type, official_level_forecast[rev_type]
            )

            if official_dates is not None and official_values is not None:
                fig_trends.add_trace(go.Scatter(
                    x=official_dates,
                    y=official_values,
                    name="2026 (Consensus Forecast)",
                    mode='lines',
                    line=dict(dash='dot', width=3, color=COLORS['secondary']),
                    opacity=0.8,
                    hovertemplate='<b>%{fullData.name}</b><br>' +
                                  'Date: %{x|%b %d, %Y}<br>' +
                                  'Consensus Forecast: $%{y:,.2f}M<br>' +
                                  '<extra></extra>'
                ))

    fig_trends.update_layout(
        xaxis_title="",
        yaxis_title="Revenue (Millions $)",
        hovermode='x unified',
        height=500,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        )
    )

    st.plotly_chart(fig_trends, use_container_width=True)

    st.markdown("---")

    # Year-over-Year Growth Rate Chart
    st.header("Year-over-Year Growth Rate (FY 2026)")
    st.caption("Chart starts October 1st to exclude noisy first quarter data")

    # Create growth rate chart
    fig_growth = go.Figure()

    # Only show FY 2026 growth rates
    growth_years = ['2026']

    for rev_type in selected_revenue_types:
        rev_data_full = df[df['rev'] == rev_type].copy()

        for year in growth_years:
            year_col = f'y{year}'

            # Need prior year to calculate growth
            year_int = int(year)
            prior_year = str(year_int - 1)
            prior_year_col = f'y{prior_year}'

            if year_col in rev_data_full.columns and prior_year_col in rev_data_full.columns:
                # Calculate YoY growth rate for each day
                growth_data = rev_data_full[['date', 'day', year_col, prior_year_col]].copy()

                # Only calculate where both years have data
                mask = (growth_data[year_col].abs() > 0.01) & (growth_data[prior_year_col].abs() > 0.01)
                growth_data = growth_data[mask].copy()

                if len(growth_data) > 0:
                    # Calculate growth rate
                    growth_data['growth_rate'] = ((growth_data[year_col] - growth_data[prior_year_col]) /
                                                   growth_data[prior_year_col] * 100)

                    # Calculate 7-day moving average
                    growth_data['growth_ma7'] = growth_data['growth_rate'].rolling(window=7, min_periods=1).mean()

                    # Filter to start at October 1st (day 93) to avoid noisy first quarter
                    # Fiscal year starts July 1 (day 1), so Oct 1 = day 93
                    growth_data = growth_data[growth_data['day'] >= 93]

                    if len(growth_data) > 0:
                        # Add actual growth rate (thinner, more transparent)
                        fig_growth.add_trace(go.Scatter(
                            x=growth_data['date'],
                            y=growth_data['growth_rate'],
                            name=f"{rev_type} - {year} (Actual)",
                            mode='lines',
                            line=dict(width=1),
                            opacity=0.4,
                            hovertemplate='<b>%{fullData.name}</b><br>' +
                                          'Date: %{x|%b %d, %Y}<br>' +
                                          'YoY Growth: %{y:.2f}%<br>' +
                                          '<extra></extra>',
                            showlegend=True
                        ))

                        # Add 7-day moving average (thicker, more prominent)
                        fig_growth.add_trace(go.Scatter(
                            x=growth_data['date'],
                            y=growth_data['growth_ma7'],
                            name=f"{rev_type} - {year} (7-day avg)",
                            mode='lines',
                            line=dict(width=3),
                            hovertemplate='<b>%{fullData.name}</b><br>' +
                                          'Date: %{x|%b %d, %Y}<br>' +
                                          '7-day Avg Growth: %{y:.2f}%<br>' +
                                          '<extra></extra>',
                            showlegend=True
                        ))

    # Add zero line
    fig_growth.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)

    # Add consensus forecast growth line if available
    if selected_revenue_type in official_growth_forecast and official_growth_forecast[selected_revenue_type] is not None:
        consensus_growth = official_growth_forecast[selected_revenue_type]
        fig_growth.add_hline(
            y=consensus_growth,
            line_dash="dot",
            line_color=COLORS['secondary'],
            line_width=3,
            opacity=0.8,
            annotation_text=f"Consensus Forecast: {consensus_growth:+.2f}%",
            annotation_position="right"
        )

    fig_growth.update_layout(
        xaxis_title="Date",
        yaxis_title="Year-over-Year Growth Rate (%)",
        hovermode='x unified',
        height=500,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        )
    )

    st.plotly_chart(fig_growth, use_container_width=True)

    # Growth Rate Comparison: Current vs Consensus Forecast
    if selected_revenue_type in official_growth_forecast and official_growth_forecast[selected_revenue_type] is not None:
        st.subheader("Growth Rate Comparison: Current vs. Consensus Forecast")
        st.caption(f"Comparing actual YoY growth with state's consensus FY26 forecast for {selected_revenue_type}")

        # Get current growth rate and 7-day moving average
        rev_data_full = df[df['rev'] == selected_revenue_type].copy()
        year_col = 'y2026'
        prior_year_col = 'y2025'

        current_growth = None
        growth_ma7 = None
        if year_col in rev_data_full.columns and prior_year_col in rev_data_full.columns:
            latest_data = rev_data_full[
                (rev_data_full[year_col].abs() > 0.01) &
                (rev_data_full[prior_year_col].abs() > 0.01)
            ].copy()

            if len(latest_data) > 0:
                latest = latest_data.iloc[-1]
                current_val = latest[year_col]
                prior_val = latest[prior_year_col]
                current_growth = ((current_val - prior_val) / prior_val) * 100

                # Calculate 7-day moving average growth rate
                latest_data['growth_rate'] = ((latest_data[year_col] - latest_data[prior_year_col]) /
                                               latest_data[prior_year_col] * 100)
                latest_data['growth_ma7'] = latest_data['growth_rate'].rolling(window=7, min_periods=1).mean()
                growth_ma7 = latest_data['growth_ma7'].iloc[-1]

        official_growth = official_growth_forecast[selected_revenue_type]
        consensus_total = official_level_forecast.get(selected_revenue_type, None)

        # Calculate probability with confidence bounds
        probability, prob_min, prob_max = calculate_average_probability(df, selected_revenue_type, consensus_total, official_growth)

        # Display comparison
        col1, col2, col3, col4 = st.columns([1, 1, 1, 2])

        with col1:
            if current_growth is not None:
                st.metric(
                    label="Current YoY Growth",
                    value=f"{current_growth:+.2f}%",
                    help="Based on latest actual data"
                )
            else:
                st.metric(label="Current YoY Growth", value="N/A")

        with col2:
            if growth_ma7 is not None:
                st.metric(
                    label="7-Day Avg Growth",
                    value=f"{growth_ma7:+.2f}%",
                    help="7-day moving average of YoY growth rate"
                )
            else:
                st.metric(label="7-Day Avg Growth", value="N/A")

        with col3:
            st.metric(
                label="Consensus Forecast",
                value=f"{official_growth:+.2f}%",
                help="State's consensus FY26 forecast"
            )

        with col4:
            if probability is not None:
                # Container with help icon overlay
                st.markdown("""
                <div class="prob-help-container">
                    <span class="prob-help-icon">
                        ?
                        <div class="prob-help-tooltip">
                            <strong>Probability Calculation Methodology:</strong><br><br>
                            The probability is calculated as an average of three independent methods:<br><br>
                            1. <strong>Model Forecast Distribution</strong>: Uses historical confidence intervals to estimate the probability based on where the consensus forecast falls within the expected range.<br><br>
                            2. <strong>Growth Rate Distribution</strong>: Analyzes historical volatility in growth rates and projects the likelihood of achieving the consensus growth rate.<br><br>
                            3. <strong>Monte Carlo Simulation</strong>: Runs 10,000 simulations using historical patterns to estimate the probability of reaching the consensus target.<br><br>
                            The final probability is the average of all three methods.
                        </div>
                    </span>
                </div>
                """, unsafe_allow_html=True)

                needle_fig = create_probability_needle(probability, selected_revenue_type, prob_min, prob_max)
                if needle_fig is not None:
                    st.plotly_chart(needle_fig, use_container_width=True)
            else:
                st.info("Probability calculation not available")

    st.markdown("---")

    # Show current growth rates for all years
    st.subheader("Current and Historical YTD Growth Rates")
    st.caption(f"Growth rates for {selected_revenue_type}")

    # Display years left to right: 2026, 2025, 2024, 2023, 2022
    display_years = ['2026', '2025', '2024', '2023', '2022']
    cols = st.columns(len(display_years))

    for idx, year in enumerate(display_years):
        rev_data_full = df[df['rev'] == selected_revenue_type].copy()

        year_col = f'y{year}'
        year_int = int(year)
        prior_year = str(year_int - 1)
        prior_year_col = f'y{prior_year}'

        with cols[idx]:
            if year_col in rev_data_full.columns and prior_year_col in rev_data_full.columns:
                # Get latest data point with values
                latest_data = rev_data_full[
                    (rev_data_full[year_col].abs() > 0.01) &
                    (rev_data_full[prior_year_col].abs() > 0.01)
                ].copy()

                if len(latest_data) > 0:
                    latest = latest_data.iloc[-1]
                    current_val = latest[year_col]
                    prior_val = latest[prior_year_col]
                    growth_pct = ((current_val - prior_val) / prior_val) * 100

                    st.metric(
                        label=f"FY {year}",
                        value=f"{growth_pct:+.2f}%",
                        delta=f"vs {prior_year}"
                    )
                else:
                    st.metric(
                        label=f"FY {year}",
                        value="N/A"
                    )
            else:
                st.metric(
                    label=f"FY {year}",
                    value="N/A"
                )


except FileNotFoundError:
    st.error("⚠️ Data file not found. Please ensure 'rev9.csv' is in the same folder as this script.")
except Exception as e:
    st.error(f"⚠️ An error occurred: {str(e)}")
    st.info("Please check your data file and try again.")

# Footer
st.markdown("---")
st.markdown("*Dashboard updated: {}*".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
