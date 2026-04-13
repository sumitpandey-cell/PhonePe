import streamlit as st
import pandas as pd
import plotly.express as px

# --- Config ---
st.set_page_config(page_title="PhonePe User Analytics", layout="wide", page_icon="👥")

# --- Custom Styling for Premium Look ---
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

def human_format(num):
    if pd.isna(num) or num == 0: return "0"
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '%.2f%s' % (num, ['', 'K', 'M', 'B', 'T', 'P'][magnitude])

# --- Data Loading ---
@st.cache_data
def load_data():
    try:
        map_user = pd.read_csv('cleaned_data/map_user.csv')
        agg_user = pd.read_csv('cleaned_data/agg_user.csv')
        return map_user, agg_user
    except Exception as e:
        st.error(f"Error loading user data: {e}")
        return pd.DataFrame(), pd.DataFrame()

map_user, agg_user = load_data()

if map_user.empty:
    st.stop()

st.title("👥 User Analytics")
st.markdown("Insights into PhonePe user registrations, app openings, and regional demographics.")

# --- Filters ---
st.sidebar.header("🔍 Global Filters")
selected_year = st.sidebar.selectbox("📅 Select Year", ["All"] + sorted(list(map_user['Year'].unique())))
selected_quarter = st.sidebar.selectbox("📊 Select Quarter", ["All"] + sorted(list(map_user['Quarter'].unique())))

map_filtered = map_user.copy()

if selected_year != "All":
    map_filtered = map_filtered[map_filtered['Year'] == selected_year]

if selected_quarter != "All":
    map_filtered = map_filtered[map_filtered['Quarter'] == selected_quarter]

# Logic to get the appropriate snapshot for cumulative user counts
if selected_year == "All" and selected_quarter == "All":
    latest_year = map_user['Year'].max()
    latest_q_in_year = map_user[map_user['Year'] == latest_year]['Quarter'].max()
    display_df = map_user[(map_user['Year'] == latest_year) & (map_user['Quarter'] == latest_q_in_year)]
elif selected_quarter == "All":
    latest_q = map_filtered['Quarter'].max()
    display_df = map_filtered[map_filtered['Quarter'] == latest_q]
else:
    display_df = map_filtered

# --- KPIs ---
st.markdown('### Key Metrics')
col1, col2, col3 = st.columns(3)

total_reg_users = display_df['Register_users'].sum()
total_app_opens = display_df['App_opens'].sum()
total_districts = map_user['District'].nunique()

with col1:
    st.markdown(create_metric_card("Total Registered Users", human_format(total_reg_users)), unsafe_allow_html=True)
with col2:
    st.markdown(create_metric_card("Total App Opens", human_format(total_app_opens)), unsafe_allow_html=True)
with col3:
    st.markdown(create_metric_card("Districts Reached", str(total_districts)), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- Charts Area 1 ---
st.markdown("### User Growth Trend")

# Aggregate registered users by Year and Quarter for trend
trend_df = map_user.groupby(['Year', 'Quarter'])['Register_users'].sum().reset_index()
trend_df['Period'] = trend_df['Year'].astype(str) + " Q" + trend_df['Quarter'].astype(str)

fig_trend = px.line(
    trend_df, 
    x='Period', 
    y='Register_users', 
    markers=True,
    text='Register_users'
)
fig_trend.update_traces(
    line_color='#6366f1', 
    line_width=3, 
    marker_size=8,
    texttemplate='%{text:.2s}',
    textposition='top center'
)
fig_trend.update_layout(
    margin=dict(t=30, b=20, l=0, r=0),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#f1f5f9'),
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
)
st.plotly_chart(fig_trend, use_container_width=True)

st.divider()

# --- Charts Area 2 ---
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.markdown("### Top 10 Districts by Users")
    top_d_df = display_df.groupby('District')['Register_users'].sum().reset_index()
    top_d_df = top_d_df.sort_values(by='Register_users', ascending=False).head(10)
    # Format district names for better readability
    top_d_df['District'] = top_d_df['District'].str.replace('_', ' ').str.title()
    
    fig_dist = px.bar(
        top_d_df, 
        x='Register_users', 
        y='District', 
        orientation='h', 
        color='Register_users', 
        color_continuous_scale='Blues',
        text_auto='.2s'
    )
    fig_dist.update_layout(
        yaxis={'categoryorder':'total ascending'}, 
        margin=dict(t=30, b=0, l=0, r=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#f1f5f9'),
        xaxis=dict(showgrid=False),
        yaxis_gridcolor='rgba(255,255,255,0.1)'
    )
    st.plotly_chart(fig_dist, use_container_width=True)

with col_chart2:
    st.markdown("### Top 10 States by App Opens")
    top_s_df = display_df.groupby('State')['App_opens'].sum().reset_index()
    top_s_df = top_s_df.sort_values(by='App_opens', ascending=False).head(10)
    top_s_df['State'] = top_s_df['State'].str.replace('_', ' ').str.replace('-', ' ').str.title()

    if top_s_df['App_opens'].sum() > 0:
        fig_state = px.bar(
            top_s_df, 
            x='State', 
            y='App_opens', 
            color='App_opens', 
            color_continuous_scale='Oranges',
            text_auto='.2s'
        )
        fig_state.update_layout(
            xaxis_type='category', 
            margin=dict(t=30, b=0, l=0, r=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#f1f5f9'),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
        )
        st.plotly_chart(fig_state, use_container_width=True)
    else:
        st.info("App opens data not available for the selected period.")