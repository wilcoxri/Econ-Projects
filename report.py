import streamlit as st
import pandas as pd
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
        ('General Fund', 'General Fund'),
        ('Income Tax Fund', 'Income Tax Fund'),
        ('Sales and Use Tax (GF)', 'Sales and Use Tax (GF)'),
        ('Sales and Use Tax (Total)', 'Sales and Use Tax (Total)'),
        ('Individual Income Tax', 'Individual Income Tax'),
        ('Corporate Tax & Gross Receipts', 'Corporate Tax & Gross Receipts'),
    ]

    # Build metrics table
    st.markdown('<div class="section-header">FY 2026 Growth Rate Summary</div>', unsafe_allow_html=True)

    table_html = """
    <table class="metric-table">
        <tr>
            <th>Revenue Source</th>
            <th>Current YTD Growth</th>
            <th>Consensus Forecast</th>
            <th>Difference</th>
        </tr>
    """

    for display_name, rev_key in revenue_types:
        current_growth = get_current_growth(df, rev_key)
        consensus_growth = official_growth_forecast.get(rev_key, None)

        current_str = f"{current_growth:+.2f}%" if current_growth is not None else "N/A"
        consensus_str = f"{consensus_growth:+.2f}%" if consensus_growth is not None else "N/A"

        if current_growth is not None and consensus_growth is not None:
            diff = current_growth - consensus_growth
            diff_class = "positive" if diff >= 0 else "negative"
            diff_str = f'<span class="{diff_class}">{diff:+.2f}%</span>'
        else:
            diff_str = "N/A"

        table_html += f"""
        <tr>
            <td><strong>{display_name}</strong></td>
            <td>{current_str}</td>
            <td>{consensus_str}</td>
            <td>{diff_str}</td>
        </tr>
        """

    table_html += "</table>"
    st.markdown(table_html, unsafe_allow_html=True)

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
