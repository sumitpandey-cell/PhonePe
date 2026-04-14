import json
from pathlib import Path
import pandas as pd
import numpy as np
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# PAGE CONFIGURATION & STYLING
# ============================================================================
st.set_page_config(
    page_title="PhonePe Analytics India 🇮🇳",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Unified CSS for Premium Dark Theme
st.markdown("""
<style>
    /* Metric Card Styling */
    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid rgba(99, 102, 241, 0.2);
        padding: 20px;
        border-radius: 12px;
        color: #f1f5f9;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s, border-color 0.2s;
        text-align: center;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        border-color: rgba(99, 102, 241, 0.5);
    }
    .metric-label {
        font-size: 14px;
        font-weight: 600;
        color: #94a3b8;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-value {
        font-size: 28px;
        font-weight: 700;
        color: #ffffff;
    }
    .metric-change {
        font-size: 12px;
        margin-top: 5px;
        color: #10b981;
    }

    /* Sidebar and general app improvements */
    [data-testid="stSidebar"] {
        background-color: #0f172a;
        border-right: 1px solid rgba(255,255,255,0.05);
    }
    .sidebar-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: #f1f5f9;
        margin-bottom: 1rem;
    }
    
    /* Global Background Adjustments */
    .stApp {
        background-color: #0f172a;
        color: #f1f5f9;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# DATA LOADING & CACHING
# ============================================================================
@st.cache_data
def load_data():
    """Load all cleaned data files with aggregated versions"""
    data_path = Path(__file__).parent.parent.parent / "cleaned_data"
    
    # Load raw data
    agg_txn = pd.read_csv(data_path / "agg_txn.csv")
    agg_user = pd.read_csv(data_path / "agg_user.csv")
    top_txn_dis = pd.read_csv(data_path / "top_txn_dis.csv")
    top_txn_pin = pd.read_csv(data_path / "top_txn_pin.csv")
    top_user_dis = pd.read_csv(data_path / "top_user_dis.csv")
    top_user_pin = pd.read_csv(data_path / "top_user_pin.csv")
    map_txn = pd.read_csv(data_path / "map_txn.csv")
    map_user = pd.read_csv(data_path / "map_user.csv")
    
    # Create aggregated versions (following map.ipynb strategy)
    agg_txn_state = agg_txn.groupby('State').agg({
        'Transaction_count': 'sum',
        'Total_amount': 'sum'
    }).reset_index()
    
    agg_user_state = agg_user.groupby('State').agg({
        'User_count': 'sum',
        'App_opens': 'sum'
    }).reset_index() if 'User_count' in agg_user.columns else agg_user.copy()
    
    return agg_txn, agg_user, top_txn_dis, top_txn_pin, top_user_dis, top_user_pin, map_txn, map_user, agg_txn_state, agg_user_state

@st.cache_data
def load_geojson():
    """Load GeoJSON file"""
    # File is in project root
    geojson_path = Path(__file__).parent / "india_state_geo.json"
    if geojson_path.exists():
        with open(geojson_path) as f:
            return json.load(f)
    return None

# ============================================================================
# DATA PROCESSING FUNCTIONS
# ============================================================================
def prepare_state_data(agg_txn, selected_state="All India"):
    """Prepare aggregated state-level data"""
    if selected_state == "All India":
        state_data = agg_txn.groupby("State").agg({
            "Transaction_count": "sum",
            "Total_amount": "sum"
        }).reset_index()
    else:
        state_data = agg_txn[agg_txn["State"] == selected_state].copy()
    
    return state_data.sort_values("Total_amount", ascending=False)

def get_yearly_trends(agg_txn, selected_state="All India"):
    """Get yearly transaction trends"""
    if selected_state == "All India":
        trends = agg_txn.groupby("Year").agg({
            "Transaction_count": "sum",
            "Total_amount": "sum"
        }).reset_index()
    else:
        trends = agg_txn[agg_txn["State"] == selected_state].groupby("Year").agg({
            "Transaction_count": "sum",
            "Total_amount": "sum"
        }).reset_index()
    
    return trends.sort_values("Year")

# ============================================================================
# VISUALIZATION FUNCTIONS
# ============================================================================
def create_metric_card(label, value, change=None):
    """Create a beautiful metric card"""
    change_html = f"<div class='metric-change'>↑ {change}% YoY</div>" if change else ""
    return f"""
    <div class='metric-card'>
        <div class='metric-label'>{label}</div>
        <div class='metric-value'>{value:,.0f}</div>
        {change_html}
    </div>
    """

def create_india_map(state_data, geojson, color_col="Total_amount", title="Transaction Value by State"):
    """Create interactive Indian state-level choropleth map"""
    
    # Mapping between PhonePe Pulse Data slugs and GeoJSON Names
    state_mapping = {
        'andaman-&-nicobar-islands': 'Andaman and Nicobar',
        'andhra-pradesh': 'Andhra Pradesh',
        'arunachal-pradesh': 'Arunachal Pradesh',
        'assam': 'Assam',
        'bihar': 'Bihar',
        'chandigarh': 'Chandigarh',
        'chhattisgarh': 'Chhattisgarh',
        'dadra-&-nagar-haveli-&-daman-&-diu': 'Dadra and Nagar Haveli',
        'delhi': 'Delhi',
        'goa': 'Goa',
        'gujarat': 'Gujarat',
        'haryana': 'Haryana',
        'himachal-pradesh': 'Himachal Pradesh',
        'jammu-&-kashmir': 'Jammu and Kashmir',
        'jharkhand': 'Jharkhand',
        'karnataka': 'Karnataka',
        'kerala': 'Kerala',
        'ladakh': 'Jammu and Kashmir',  # Mapping to J&K in older GeoJSON
        'lakshadweep': 'Lakshadweep',
        'madhya-pradesh': 'Madhya Pradesh',
        'maharashtra': 'Maharashtra',
        'manipur': 'Manipur',
        'meghalaya': 'Meghalaya',
        'mizoram': 'Mizoram',
        'nagaland': 'Nagaland',
        'odisha': 'Orissa',            # Match GeoJSON name
        'puducherry': 'Puducherry',
        'punjab': 'Punjab',
        'rajasthan': 'Rajasthan',
        'sikkim': 'Sikkim',
        'tamil-nadu': 'Tamil Nadu',
        'telangana': 'Andhra Pradesh',  # Mapping to AP in older GeoJSON
        'tripura': 'Tripura',
        'uttar-pradesh': 'Uttar Pradesh',
        'uttarakhand': 'Uttaranchal',    # Match GeoJSON name
        'west-bengal': 'West Bengal'
    }
    
    # Prepare data for map
    map_df = state_data.copy()
    map_df['GeoState'] = map_df['State'].map(state_mapping)
    
    # Map Visualization
    fig = px.choropleth(
        map_df,
        geojson=geojson,
        featureidkey="properties.NAME_1",
        locations="GeoState",
        color=color_col,
        hover_name="State",
        hover_data={"Total_amount": ":,.2f", "Transaction_count": ":,", "GeoState": False},
        color_continuous_scale=[
            [0, '#1e293b'],
            [0.2, '#312e81'],
            [0.4, '#4f46e5'],
            [1, '#ec4899']
        ],
        labels={"Total_amount": "Amount (₹)", "Transaction_count": "Count"}
    )
    
    fig.update_geos(fitbounds="locations", visible=False)
    
    fig.update_layout(
        title={'text': f"<b>{title}</b>", 'x':0.5, 'xanchor': 'center', 'font': {'size': 18, 'color': '#f1f5f9'}},
        margin={"r":0,"t":80,"l":0,"b":0},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#f1f5f9'),
        height=700,
        coloraxis_colorbar=dict(
            title="Amount (₹)",
            thickness=15,
            len=0.7,
            bgcolor='rgba(31, 41, 55, 0.3)',
            bordercolor='rgba(99, 102, 241, 0.3)',
            borderwidth=1,
            tickfont=dict(color='#f1f5f9')
        )
    )
    
    return fig

def create_district_treemap(district_data, title="District-wise Transaction Distribution"):
    """Create a premium treemap for district-level visualization"""
    # Clean up names for display
    plot_df = district_data.copy()
    plot_df['Display_State'] = plot_df['State'].str.replace('-', ' ').str.title()
    plot_df['Display_District'] = plot_df['District'].str.title()
    
    fig = px.treemap(
        plot_df,
        path=[px.Constant("India"), 'Display_State', 'Display_District'],
        values='Total_amount',
        color='Total_amount',
        color_continuous_scale='Magma',
        hover_data={'Total_amount': ':,.2f', 'Transaction_count': ':,'},
    )
    
    fig.update_layout(
        title={'text': f"<b>{title}</b>", 'x':0.5, 'xanchor': 'center', 'font': {'size': 18, 'color': '#f1f5f9'}},
        margin=dict(t=80, b=20, l=20, r=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#f1f5f9'),
        height=650
    )
    
    return fig

# ============================================================================
# MAIN APP
# ============================================================================
def main():
    # Load data
    agg_txn, agg_user, top_txn_dis, top_txn_pin, top_user_dis, top_user_pin, map_txn, map_user, agg_txn_state, agg_user_state = load_data()
    geojson_data = load_geojson()
    
    # Normalize state names
    for df in [agg_txn, top_txn_dis, top_txn_pin]:
        df["State"] = df["State"].str.strip()
    
    # ========================================================================
    # SIDEBAR CONTROLS
    # ========================================================================
    with st.sidebar: 
        st.markdown("<div class='sidebar-title'>🎛️ Controls</div>", unsafe_allow_html=True)
        
        unique_states = ["All India"] + sorted(agg_txn["State"].unique().tolist())
        selected_state = st.selectbox(
                "Select Region",
                unique_states,
                key="state_select"
            )
            
        st.markdown("---")
        st.markdown("<div class='sidebar-title'>📈 Analytics Period</div>", unsafe_allow_html=True)
            
        year_range = st.slider(
                "Select Years",
                int(agg_txn["Year"].min()),
                int(agg_txn["Year"].max()),
                (int(agg_txn["Year"].min()), int(agg_txn["Year"].max())),
                key="year_slider"
            )
            
        st.markdown("---")
        
        # Filter data by year range
        filtered_agg_txn = agg_txn[(agg_txn["Year"] >= year_range[0]) & (agg_txn["Year"] <= year_range[1])]
    
    # ========================================================================
    # KPI CARDS
    # ========================================================================
    st.markdown("### 💰 Key Performance Indicators")
    
    if selected_state == "All India":
        kpi_data = filtered_agg_txn.groupby("State").agg({
            "Transaction_count": "sum",
            "Total_amount": "sum"
        }).reset_index()
        total_txn = filtered_agg_txn["Transaction_count"].sum()
        total_amount = filtered_agg_txn["Total_amount"].sum()
    else:
        kpi_data = filtered_agg_txn[filtered_agg_txn["State"] == selected_state]
        total_txn = kpi_data["Transaction_count"].sum()
        total_amount = kpi_data["Total_amount"].sum()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(create_metric_card("Total Transactions", total_txn, 12), unsafe_allow_html=True)
    with col2:
        st.markdown(create_metric_card("Value (₹ Cr)", total_amount / 1e7, 18), unsafe_allow_html=True)
    with col3:
        avg_val = (total_amount / total_txn) if total_txn > 0 else 0
        st.markdown(create_metric_card("Avg Value", avg_val, 5), unsafe_allow_html=True)
    with col4:
        if selected_state == "All India":
            states = filtered_agg_txn["State"].nunique()
            st.markdown(create_metric_card("States/UTs", states, 0), unsafe_allow_html=True)
        else:
            district_count = top_txn_dis[top_txn_dis["State"] == selected_state]["District"].nunique()
            st.markdown(create_metric_card("Districts", district_count, 0), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ========================================================================
    # INTERACTIVE MAP
    # ========================================================================
    st.markdown("### 🗺️ Geographic Distribution - Indian State Boundaries")
    
    if geojson_data:
        # Prepare state-level data for the map
        state_map_data = filtered_agg_txn.groupby("State").agg({
            "Transaction_count": "sum",
            "Total_amount": "sum"
        }).reset_index()
        
        map_title = f"India Transaction Value (₹) - {year_range[0]} to {year_range[1]}"
        india_map = create_india_map(state_map_data, geojson_data, title=map_title)
        st.plotly_chart(india_map, use_container_width=True)
    else:
        st.warning("GeoJSON file not found. Map cannot be displayed.")
    
    st.markdown("---")
    
    # ========================================================================
    # DISTRICT-LEVEL ANALYSIS (TREEMAP)
    # ========================================================================
    st.markdown("### 📊 District-wise Transaction Distribution")
    
    # Filter district data by year and state
    district_filtered = top_txn_dis[(top_txn_dis["Year"] >= year_range[0]) & (top_txn_dis["Year"] <= year_range[1])]
    
    if selected_state != "All India":
        district_filtered = district_filtered[district_filtered["State"] == selected_state]
    
    if not district_filtered.empty:
        treemap_title = f"District Performance - {selected_state} ({year_range[0]}-{year_range[1]})"
        treemap_fig = create_district_treemap(district_filtered, title=treemap_title)
        st.plotly_chart(treemap_fig, use_container_width=True)
    else:
        st.info("No district data available for the selected filters.")
    
    st.markdown("---")
    
    # ========================================================================
    # FOOTER
    # ========================================================================
    st.markdown("""
    <div style='text-align: center; color: #64748b; padding: 20px; margin-top: 40px;'>
        <small>
            📊 PhonePe Analytics Dashboard | Indian Payment Strategy Visualization
        </small>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
