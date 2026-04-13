# PhonePe Data Analytics Project 📊

A comprehensive data analysis and visualization project of PhonePe's digital payment transactions and user metrics across India. This project extracts raw JSON data, performs data cleaning and analysis, and provides an interactive Streamlit dashboard for insights.

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Project Structure](#project-structure)
- [Data Description](#data-description)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Notebooks & Analysis](#notebooks--analysis)
- [Dashboard Features](#dashboard-features)
- [Technologies Used](#technologies-used)
- [License](#license)

## 🎯 Project Overview

This project analyzes PhonePe's digital payment ecosystem in India with focus on:

- **Transaction Analysis**: Payment volumes, trends, and patterns across states, districts, and pincodes
- **User Analytics**: Device-wise user distribution and adoption patterns
- **Insurance Metrics**: Insurance transaction data and trends
- **Geospatial Visualization**: State-level and district-level insights on India's map
- **Time-Series Analysis**: Quarter-wise trends from 2018 to 2024

The data is sourced from PhonePe's public datasets and processed to create actionable business intelligence.

## 📁 Project Structure

```
PhonePe/
├── README.md                          # This file
├── .gitignore                         # Git ignore file
├── Data_extraction.ipynb              # Raw data extraction & processing notebook
├── cleaned_data_analysis.ipynb        # Data analysis and exploration notebook
│
├── cleaned_data/                      # Processed & cleaned CSV files
│   ├── agg_txn.csv                    # Aggregated transaction data
│   ├── agg_user.csv                   # Aggregated user data
│   ├── map_txn.csv                    # Map transaction data
│   ├── map_user.csv                   # Map user data
│   ├── top_txn_dis.csv                # Top transactions by district
│   ├── top_txn_pin.csv                # Top transactions by pincode
│   ├── top_user_dis.csv               # Top users by district
│   └── top_user_pin.csv               # Top users by pincode
│
├── India_State_Boundary/              # Geospatial data
│   ├── India_State_Boundary.shp       # Shapefile for India states
│   ├── India_State_Boundary.dbf
│   ├── India_State_Boundary.prj
│   ├── India_State_Boundary.cpg
│   └── [other shapefile components]
│
└── streamlit_app/                     # Interactive dashboard
    ├── overview.py                    # Dashboard home page
    ├── india_state_geo.json           # GeoJSON for map visualization
    └── pages/
        ├── 1_Transactions.py          # Transaction analytics page
        └── 2_Users.py                 # User analytics page
```

## 📊 Data Description

### Cleaned Datasets

| File | Description | Records |
|------|-------------|---------|
| `agg_txn.csv` | State-level transaction aggregates | Multiple quarters, all states |
| `agg_user.csv` | State-level user data by device brand | Device-wise breakdown |
| `map_txn.csv` | District/pincode-level transaction mapping | Detailed geographic data |
| `map_user.csv` | District/pincode-level user distribution | User geographic spread |
| `top_txn_dis.csv` | Top districts by transaction count | Ranked districts |
| `top_txn_pin.csv` | Top pincodes by transaction count | Ranked pincodes |
| `top_user_dis.csv` | Top districts by user count | Ranked districts |
| `top_user_pin.csv` | Top pincodes by user count | Ranked pincodes |

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- pip or conda
- Git

### Installation

1. **Clone or navigate to the project directory**
   ```bash
   cd PhonePe
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   ```

3. **Activate the virtual environment**
   - On Windows:
     ```bash
     .venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```

4. **Install required dependencies**
   ```bash
   pip install -r requirements.txt
   ```

   Or install packages manually:
   ```bash
   pip install pandas numpy geopandas plotly streamlit matplotlib seaborn
   ```

## 📖 Usage

### 1. Data Analysis

Explore cleaned data with the analysis notebook:

```bash
jupyter notebook cleaned_data_analysis.ipynb
```

This notebook provides:
- Data overview and statistics
- Exploratory data analysis (EDA)
- Trend analysis
- Validation checks

### 2. Interactive Dashboard

Launch the Streamlit dashboard for interactive exploration:

```bash
streamlit run streamlit_app/overview.py
```

The dashboard opens in your browser at `http://localhost:8501/` with:
- **Overview Page**: Key metrics and trends
- **Transactions Page**: Detailed transaction analytics
- **Users Page**: User adoption and device trends

## 📓 Notebooks & Analysis

### Data_extraction.ipynb

**Purpose**: Extract and process raw PhonePe JSON data (Optional)

**Note**: This notebook is used to process raw JSON files from the PhonePe public dataset. Since the raw `data/` folder is not included in this repository, you can skip this step if you're using the pre-processed cleaned CSV files.

**Key Steps** (when raw data is available):
- Traverse the hierarchical data structure (data type → category → state → year → quarter)
- Extract relevant fields from nested JSON
- Convert to structured pandas DataFrames
- Export to cleaned CSV files

**Output**: Cleaned CSV datasets ready for analysis

### cleaned_data_analysis.ipynb

**Purpose**: Analyze processed data and generate insights

**Key Analysis**:
- Aggregate metrics by state, district, and pincode
- Calculate growth rates and trends
- Device brand distribution analysis
- Geographic distribution patterns
- Quarterly and yearly comparisons

**Output**: Summary statistics and validation

## 📈 Dashboard Features

### Overview Page (`overview.py`)

- Total transactions and users cards
- Transaction and user trend charts
- Top states by activity
- Quarter-wise progress metrics
- Premium dark-themed UI

### Transactions Page (`1_Transactions.py`)

- State-level transaction heatmaps
- District and pincode rankings
- Quarterly trend analysis
- Geographic visualization using GeoDataFrame
- Filter options by time period and location

### Users Page (`2_Users.py`)

- User adoption trends
- Device brand distribution
- Geographic user distribution
- Top performing states and districts
- Mobile brand market share analysis

## 🛠️ Technologies Used

- **Data Processing**: pandas, numpy
- **Geospatial**: geopandas, shapely
- **Visualization**: plotly, matplotlib, seaborn
- **Web Dashboard**: streamlit
- **Data Format**: JSON, CSV, Shapefile
- **Python Version**: 3.8+

## 📝 Data Notes

- **Time Range**: Q1 2018 - Q4 2024 (transactions), 2020-2024 (insurance)
- **Geographic Coverage**: All states and union territories of India
- **Granularity**: State, district, and pincode levels
- **Data Type**: Aggregated metrics (no PII included)
- **Data Source**: PhonePe Public Datasets
- **Raw Data**: Not included in repository (available at [PhonePe Data](https://www.phonepedata.com/))

## 🤝 Contributing

This is a personal data analysis project. Feel free to fork and adapt for your own use.

## 📄 License

This project uses public PhonePe dataset. Ensure compliance with PhonePe's data usage terms.

## 🔗 Resources

- [PhonePe Public Datasets](https://www.phonepedata.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Plotly Documentation](https://plotly.com/python/)
- [GeoPandas Documentation](https://geopandas.org/)

---

**Last Updated**: April 2026  
**Project Status**: Active
