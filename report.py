import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# Page configuration - optimized for printing
st.set_page_config(
    page_title="Revenue Report",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Print-friendly CSS
st.markdown("""
<style>
    /* Hide Streamlit elements for printing */
    @media print {
        .stApp header, .stApp footer, [data-testid="stToolbar"],
        [data-testid="stDecoration"], [data-testid="stStatusWidget"],
        .stTextArea label, button, [data-testid="stSidebar"] {
            display: none !important;
        }
        .main .block-container {
            padding: 0 !important;
            max-width: 100% !important;
        }
    }

    /* General styling */
    .report-title {
        font-size: 24px;
        font-weight: bold;
        color: #112347;
        text-align: center;
        margin-bottom: 5px;
    }
    .report-date {
        font-size: 14px;
        color: #666;
        text-align: center;
        margin-bottom: 20px;
    }
    .section-header {
        font-size: 16px;
        font-weight: bold;
        color: #112347;
        border-bottom: 2px solid #112347;
        padding-bottom: 5px;
        margin-top: 20px;
        margin-bottom: 10px;
    }
    .commentary-box {
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 15px;
        min-height: 120px;
        background-color: #fafafa;
        font-size: 13px;
    }
    .metric-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
    }
    .metric-table th {
        background-color: #112347;
        color: white;
        padding: 8px;
        text-align: left;
    }
    .metric-table td {
        padding: 8px;
        border-bottom: 1px solid #ddd;
    }
    .metric-table tr:nth-child(even) {
        background-color: #f9f9f9;
    }
    .positive { color: #2ecc71; }
    .negative { color: #e74c3c; }
</style>
""", unsafe_allow_html=True)

# Load data functions (same as main dashboard)
@st.cache_data
def load_official_forecast():
    try:
        forecast_df = pd.read_csv('FY26 forecast.csv')
        forecast_df.columns = forecast_df.columns.str.strip()
        forecast_df['Rev'] = forecast_df['Rev'].str.strip()
        forecast_df['Level Forecast'] = forecast_df['Level Forecast'].str.replace(',', '').str.strip()
        forecast_df['Level Forecast'] = pd.to_numeric(forecast_df['Level Forecast'], errors='coerce')
        forecast_df['Growth Forecast'] = forecast_df['Growth Forecast'].str.replace('%', '').str.strip()
        forecast_df['Growth Forecast'] = pd.to_numeric(forecast_df['Growth Forecast'], errors='coerce')
        level_forecast = dict(zip(forecast_df['Rev'], forecast_df['Level Forecast']))
        growth_forecast = dict(zip(forecast_df['Rev'], forecast_df['Growth Forecast']))
        return level_forecast, growth_forecast
    except FileNotFoundError:
        return {}, {}

@st.cache_data
def load_data():
    df = pd.read_csv('rev9.csv', thousands=',')
    df['date'] = pd.to_datetime(df['date'], format='%d%b%Y')
    year_cols = [col for col in df.columns if col.startswith('y')]

    for col in year_cols:
        if df[col].dtype == 'object':
            df[col] = df[col].str.replace(',', '')
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df[year_cols] = df[year_cols].fillna(0)

    # Create Individual Income Tax
    income_tax_components = ['Withholding', 'Gross Payments', 'Refunds']
    component_data = df[df['rev'].isin(income_tax_components)].copy()
    if len(component_data) > 0:
        income_tax_data = component_data.groupby(['day', 'date']).agg({
            **{col: 'sum' for col in year_cols}
        }).reset_index()
        income_tax_data['rev'] = 'Individual Income Tax'
        income_tax_data = income_tax_data[['rev', 'day', 'date'] + year_cols]
        df = pd.concat([df, income_tax_data], ignore_index=True)

    # Create Sales and Use Tax (GF)
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

    # Create General Fund
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

    # Create Income Tax Fund
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

    return df, year_cols

def get_current_growth(df, rev_type):
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

def get_last_data_date(df, rev_type):
    rev_type_data = df[df['rev'] == rev_type].copy()
    year_col = 'y2026'

    if year_col in rev_type_data.columns:
        latest_data = rev_type_data[rev_type_data[year_col].abs() > 0.01]
        if len(latest_data) > 0:
            return latest_data.iloc[-1]['date']
    return None

def calculate_probability_method1(df, rev_type, consensus_total):
    """Method 1: Model Forecast Distribution"""
    from scipy import stats
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

    if rev_data[prior_year_col].mean() < 0:
        prior_year_total = rev_data[prior_year_col].min()
    else:
        prior_year_total = rev_data[prior_year_col].max()
    prior_year_remaining = prior_year_total - prior_value
    forecast_total = last_actual_value + (prior_year_remaining * (1 + growth_rate))
    forecast_std = prior_year_remaining * growth_std

    if forecast_std <= 0:
        return None

    z_score = (consensus_total - forecast_total) / forecast_std
    probability = (1 - stats.norm.cdf(z_score)) * 100

    return probability

def calculate_probability_method2(df, rev_type, consensus_growth):
    """Method 2: Growth Rate Distribution"""
    from scipy import stats
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

    historical_years = ['2022', '2023', '2024', '2025']
    historical_growth_rates = []

    for i in range(len(historical_years) - 1):
        y1, y2 = historical_years[i], historical_years[i + 1]
        col1, col2 = f'y{y1}', f'y{y2}'

        if col1 in rev_data.columns and col2 in rev_data.columns:
            if rev_data[col1].mean() < 0:
                total1 = rev_data[col1].min()
                total2 = rev_data[col2].min()
            else:
                total1 = rev_data[col1].max()
                total2 = rev_data[col2].max()
            if abs(total1) > 0.01:
                historical_growth_rates.append((total2 - total1) / total1 * 100)

    growth_std = np.std(historical_growth_rates) if len(historical_growth_rates) > 1 else 5.0

    total_days = 365
    days_remaining = total_days - last_actual_day
    time_factor = np.sqrt(days_remaining / total_days)
    adjusted_std = growth_std * time_factor

    if adjusted_std <= 0:
        return None

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
    if rev_data[prior_year_col].mean() < 0:
        prior_year_total = rev_data[prior_year_col].min()
    else:
        prior_year_total = rev_data[prior_year_col].max()

    if abs(prior_value) < 0.01:
        return None

    current_growth = (last_actual_value - prior_value) / prior_value

    historical_years = ['2022', '2023', '2024', '2025']
    historical_growth_rates = []

    for i in range(len(historical_years) - 1):
        y1, y2 = historical_years[i], historical_years[i + 1]
        col1, col2 = f'y{y1}', f'y{y2}'

        if col1 in rev_data.columns and col2 in rev_data.columns:
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
    """Calculate average probability across three methods"""
    if consensus_total is None or consensus_growth is None:
        return None

    prob1 = calculate_probability_method1(df, rev_type, consensus_total)
    prob2 = calculate_probability_method2(df, rev_type, consensus_growth)
    prob3 = calculate_probability_method3(df, rev_type, consensus_total)

    valid_probs = [p for p in [prob1, prob2, prob3] if p is not None]
    if len(valid_probs) > 0:
        return np.mean(valid_probs)
    return None

def get_status_html(probability):
    """Create a simple HTML status indicator for PDF-friendly output"""
    if probability is None:
        return "N/A"

    # Determine status and color
    if probability < 50:
        status = "Below Target"
        color = "#e74c3c"  # Red
        bg_color = "#ffebee"
    elif probability <= 75:
        status = "On Target"
        color = "#f39c12"  # Orange
        bg_color = "#fff8e1"
    else:
        status = "Above Target"
        color = "#2ecc71"  # Green
        bg_color = "#e8f5e9"

    return f'<div style="background-color: {bg_color}; color: {color}; padding: 8px 12px; border-radius: 5px; text-align: center; font-weight: bold; border: 2px solid {color};">{status}</div>'

# Load data
try:
    df, year_cols = load_data()
    official_level_forecast, official_growth_forecast = load_official_forecast()

    # Get the latest data date
    last_date = get_last_data_date(df, 'General Fund')
    last_date_str = last_date.strftime('%B %d, %Y') if last_date else 'N/A'

    # Report Header
    st.markdown(f'<div class="report-title">GOPB Revenue Collections Report</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="report-date">FY 2026 Year-to-Date through {last_date_str}</div>', unsafe_allow_html=True)

    # Revenue types to display
    revenue_types = [
        ('Sales and Use Tax (Total)', 'Sales and Use Tax (Total)'),
        ('Sales and Use Tax (GF)', 'Sales and Use Tax (GF)'),
        ('General Fund', 'General Fund'),
        ('Individual Income Tax', 'Individual Income Tax'),
        ('Corporate Tax & Gross Receipts', 'Corporate Tax & Gross Receipts'),
        ('Income Tax Fund', 'Income Tax Fund'),
    ]

    # Build metrics table
    st.markdown('<div class="section-header">FY 2026 Growth Rate Summary</div>', unsafe_allow_html=True)

    # Column headers
    header_col1, header_col2, header_col3, header_col4 = st.columns([2, 1, 1, 1.5])
    with header_col1:
        st.markdown("**Revenue Source**")
    with header_col2:
        st.markdown("**Current YTD**")
    with header_col3:
        st.markdown("**Forecast**")
    with header_col4:
        st.markdown("**Status**")

    st.markdown("<hr style='margin: 5px 0; border: 1px solid #112347;'>", unsafe_allow_html=True)

    # Display each revenue type as a row with gauge
    for i, (display_name, rev_key) in enumerate(revenue_types):
        current_growth = get_current_growth(df, rev_key)
        consensus_growth = official_growth_forecast.get(rev_key, None)
        consensus_total = official_level_forecast.get(rev_key, None)

        current_str = f"{current_growth:+.2f}%" if current_growth is not None else "N/A"
        consensus_str = f"{consensus_growth:+.2f}%" if consensus_growth is not None else "N/A"

        # Calculate probability
        probability = calculate_average_probability(df, rev_key, consensus_total, consensus_growth)

        # Create row with 4 columns
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1.5])

        with col1:
            st.markdown(f"**{display_name}**")
        with col2:
            st.markdown(current_str)
        with col3:
            st.markdown(consensus_str)
        with col4:
            status_html = get_status_html(probability)
            st.markdown(status_html, unsafe_allow_html=True)

        # Add separator line between rows
        st.markdown("<hr style='margin: 2px 0; border: 0.5px solid #ddd;'>", unsafe_allow_html=True)

    st.markdown("---")

    # Commentary sections
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header">General Fund Commentary</div>', unsafe_allow_html=True)
        gf_commentary = st.text_area(
            "General Fund Commentary",
            value="• \n• \n• ",
            height=150,
            label_visibility="collapsed",
            key="gf_commentary"
        )

    with col2:
        st.markdown('<div class="section-header">Income Tax Fund Commentary</div>', unsafe_allow_html=True)
        itf_commentary = st.text_area(
            "Income Tax Fund Commentary",
            value="• \n• \n• ",
            height=150,
            label_visibility="collapsed",
            key="itf_commentary"
        )

    # Print instructions
    st.markdown("---")
    st.markdown("**To save as PDF:** Press `Ctrl+P` (or `Cmd+P` on Mac), select 'Save as PDF' as the destination.")

except FileNotFoundError:
    st.error("Data files not found. Please ensure 'rev9.csv' and 'FY26 forecast.csv' are in the same directory.")
except Exception as e:
    st.error(f"An error occurred: {str(e)}")
