import streamlit as st
import pandas as pd
import plotly.express as px

# --- Config ---
st.set_page_config(page_title="PhonePe Data Overview", layout="wide", page_icon="💸")

# --- Custom Styling for Premium Look ---
st.markdown("""`
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
        margin-bottom: 15px;
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
        font-size: 24px;
        font-weight: 700;
        color: #ffffff;
    }

    /* Sidebar and general app improvements */
    [data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid rgba(255,255,255,0.05);
    }
    .stApp {
        background-color: #0f172a;
        color: #f1f5f9;
    }
    h1, h2, h3, h4 {
        color: #f1f5f9 !important;
    }
</style>
""", unsafe_allow_html=True)

# Helper function for metric cards
def create_metric_card(label, value):
    return f"""
    <div class='metric-card'>
        <div class='metric-label'>{label}</div>
        <div class='metric-value'>{value}</div>
    </div>
    """

# Helper function to format large numbers
def human_format(num):
    if num == 0: return "0"
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '%.2f%s' % (num, ['', 'K', 'M', 'B', 'T', 'P'][magnitude])

# --- Data Loading ---
@st.cache_data
def load_data():
    try:
        agg_txn = pd.read_csv('cleaned_data/agg_txn.csv')
        agg_user = pd.read_csv('cleaned_data/agg_user.csv')
        return agg_txn, agg_user
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame(), pd.DataFrame()

agg_txn, agg_user = load_data()

if agg_txn.empty and agg_user.empty:
    st.stop()

# --- Main UI ---
st.title("💸 PhonePe Pulse - Dashboard Overview")
st.markdown("A dynamic dashboard providing insights into PhonePe transactions and user devices across India.")

# --- Sidebar Filters ---
st.sidebar.header("🔍 Global Filters")
selected_year = st.sidebar.selectbox("📅 Select Year", ["All"] + sorted(list(agg_txn['Year'].unique())))
selected_quarter = st.sidebar.selectbox("📊 Select Quarter", ["All"] + sorted(list(agg_txn['Quarter'].unique())))

# Apply filters
txn_filtered = agg_txn.copy()
user_filtered = agg_user.copy()

if selected_year != "All":
    txn_filtered = txn_filtered[txn_filtered['Year'] == selected_year]
    user_filtered = user_filtered[user_filtered['Year'] == selected_year]

if selected_quarter != "All":
    txn_filtered = txn_filtered[txn_filtered['Quarter'] == selected_quarter]
    user_filtered = user_filtered[user_filtered['Quarter'] == selected_quarter]


# --- KPIs ---
st.markdown('### Key Performance Indicators')
col1, col2, col3 = st.columns(3)

total_txns = txn_filtered['Transaction_count'].sum()
total_amount = txn_filtered['Total_amount'].sum()
user_val = "N/A"
if 'Count' in user_filtered.columns:
    user_val = human_format(user_filtered['Count'].sum())

with col1:
    st.markdown(create_metric_card("Total Transactions", human_format(total_txns)), unsafe_allow_html=True)
with col2:
    st.markdown(create_metric_card("Total Amount (₹)", human_format(total_amount)), unsafe_allow_html=True)
with col3:
    st.markdown(create_metric_card("Device Interactions", user_val), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- Charts Area 1 ---
st.markdown('### Transaction Analytics')
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.markdown("#### Transactions By Type")
    txn_type_grp = txn_filtered.groupby('Transaction_type')['Transaction_count'].sum().reset_index()
    fig_pie = px.pie(
        txn_type_grp, 
        values='Transaction_count', 
        names='Transaction_type', 
        hole=0.4, 
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_pie.update_layout(
        margin=dict(t=30, b=0, l=0, r=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#f1f5f9'),
        legend=dict(font=dict(color='#f1f5f9'))
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with chart_col2:
    if selected_year == "All":
        st.markdown("#### Transaction Trend Over Years")
        txn_trend = agg_txn.groupby(['Year'])['Transaction_count'].sum().reset_index()
        fig_bar = px.bar(
            txn_trend, x='Year', y='Transaction_count',
            color='Transaction_count', color_continuous_scale='Viridis',
            text_auto='.2s'
        )
        fig_bar.update_layout(
            xaxis_type='category', 
            margin=dict(t=30, b=0, l=0, r=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#f1f5f9'),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.markdown(f"#### Transaction Trend Across Quarters in {selected_year}")
        txn_trend = agg_txn[agg_txn['Year'] == selected_year].groupby(['Quarter'])['Transaction_count'].sum().reset_index()
        fig_bar = px.bar(
            txn_trend, x='Quarter', y='Transaction_count',
            color='Transaction_count', color_continuous_scale='Viridis',
            text_auto='.2s'
        )
        fig_bar.update_layout(
            xaxis_type='category', 
            margin=dict(t=30, b=0, l=0, r=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#f1f5f9'),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
        )
        st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- Charts Area 2 ---
st.markdown('### User Device Preferences')
user_brand_grp = user_filtered[user_filtered['Brand'] != 'Unknown']
user_brand_grp = user_brand_grp.groupby('Brand')['Count'].sum().reset_index().sort_values(by='Count', ascending=False)
fig_brand = px.bar(
    user_brand_grp.head(10), 
    x='Brand', 
    y='Count', 
    text_auto='.2s', 
    color='Count', 
    color_continuous_scale='Cividis'
)
fig_brand.update_layout(
    margin=dict(t=30, b=0, l=0, r=0),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#f1f5f9'),
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
)
st.plotly_chart(fig_brand, use_container_width=True)
