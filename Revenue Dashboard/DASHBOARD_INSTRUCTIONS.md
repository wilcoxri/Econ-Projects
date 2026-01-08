# State Revenue Collections Dashboard

## Setup Instructions

### Step 1: Install Python (if not already installed)
- Download Python 3.10 or later from https://www.python.org/downloads/
- During installation, make sure to check "Add Python to PATH"

### Step 2: Install Required Packages
Open Command Prompt or PowerShell and navigate to your Desktop:

```bash
cd C:\Users\rwilcox\Desktop
pip install -r requirements.txt
```

Alternatively, install packages individually:
```bash
pip install streamlit pandas plotly openpyxl
```

### Step 3: Run the Dashboard
Make sure both `revenue_dashboard.py` and `rev9.csv` are in the same folder (Desktop), then run:

```bash
streamlit run revenue_dashboard.py
```

The dashboard will open automatically in your default web browser at `http://localhost:8501`

## Dashboard Features

### Interactive Filters (Left Sidebar)
1. **Revenue Type Selection**: Choose one or more revenue sources to analyze
2. **Date Range**: Select specific time periods
3. **Year Comparison**: Pick which years to compare (2010-2026)
4. **View Type**: Switch between daily, cumulative, or month-to-date views

### Visualizations
1. **Key Metrics**: Top-level summary showing total revenue for each selected year
2. **Revenue Trends Over Time**: Line chart showing daily/monthly trends
3. **Year-over-Year Comparison**: Bar charts comparing revenue across years
4. **Monthly Averages**: Track monthly patterns
5. **Revenue Category Breakdown**: Pie chart showing distribution of revenue sources
6. **Data Table**: Searchable, sortable table of filtered data
7. **Export Function**: Download filtered data as CSV

## Tips for Decision Makers

### Quick Analysis Examples
- **Compare current year to last year**: Select only 2025 and 2026 in the year filter
- **View top revenue sources**: Look at the pie chart and metrics on the right
- **Track monthly trends**: Use the Monthly Average Comparison chart
- **Identify patterns**: Use the time series chart to spot seasonal trends

### Sharing the Dashboard
- **Share locally**: Run on your computer and share your screen
- **Deploy to server**: Contact IT to host on state servers
- **Create snapshots**: Use browser screenshot tools or export charts

### Updating Data
Simply replace `rev9.csv` with updated data (keeping the same format) and refresh the dashboard.

## Troubleshooting

**Dashboard won't start?**
- Make sure Python is installed: `python --version`
- Make sure packages are installed: `pip list`
- Check that both `revenue_dashboard.py` and `rev9.csv` are in the same folder

**Data not loading?**
- Verify `rev9.csv` is in the same directory as the Python script
- Check that the CSV format matches the expected structure

**Need help?**
- Streamlit documentation: https://docs.streamlit.io
- For custom modifications, edit `revenue_dashboard.py`

## System Requirements
- Windows 10/11
- Python 3.10 or later
- 4GB RAM minimum (8GB recommended)
- Modern web browser (Chrome, Firefox, Edge)
