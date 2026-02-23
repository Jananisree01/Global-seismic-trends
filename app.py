# ==========================================
# GLOBAL SEISMIC TRENDS – STREAMLIT DASHBOARD
# ==========================================

import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from urllib.parse import quote_plus

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(page_title="Global Seismic Trends", layout="wide")

st.title("🌍 Global Seismic Trends Dashboard")
st.markdown("### Data-Driven Earthquake Insights")

# ----------------------------
# DATABASE CONNECTION
# ----------------------------

# 🔐 Replace with your real MySQL password
password = quote_plus("Nithik@20")  

engine = create_engine(
    f"mysql+pymysql://root:{password}@localhost:3306/seismic_db"
)

@st.cache_data
def load_data(query):
    return pd.read_sql(query, engine)

# ----------------------------
# SIDEBAR FILTERS
# ----------------------------

st.sidebar.header("🔎 Filters")

year_query = """
SELECT DISTINCT YEAR(time) as year
FROM earthquakes
ORDER BY year
"""

years = load_data(year_query)

selected_year = st.sidebar.selectbox("Select Year", years["year"])

min_mag = st.sidebar.slider("Minimum Magnitude", 0.0, 10.0, 4.0)

# ----------------------------
# KPI SECTION
# ----------------------------

kpi_query = f"""
SELECT COUNT(*) as total_eq,
       AVG(mag) as avg_mag,
       MAX(mag) as max_mag
FROM earthquakes
WHERE YEAR(time) = {selected_year}
AND mag >= {min_mag}
"""

kpi = load_data(kpi_query)

col1, col2, col3 = st.columns(3)

col1.metric("Total Earthquakes", int(kpi["total_eq"][0]))
col2.metric("Average Magnitude", round(kpi["avg_mag"][0], 2))
col3.metric("Maximum Magnitude", round(kpi["max_mag"][0], 2))

st.divider()

# ----------------------------
# TABS
# ----------------------------

tab1, tab2, tab3, tab4 = st.tabs(
    ["📊 Time Analysis",
     "🔥 Magnitude & Depth",
     "🌊 Tsunami & Alerts",
     "📍 Quality Metrics"]
)

# =====================================
# TAB 1 – TIME ANALYSIS
# =====================================

with tab1:

    st.subheader("Year-wise Earthquake Count")

    df_year = load_data("""
    SELECT YEAR(time) as year,
           COUNT(*) as total
    FROM earthquakes
    GROUP BY YEAR(time)
    ORDER BY year
    """)

    fig_year = px.line(df_year, x="year", y="total",
                       markers=True,
                       title="Earthquakes Per Year")

    st.plotly_chart(fig_year, use_container_width=True)

    st.subheader("Monthly Earthquake Distribution")

    df_month = load_data("""
    SELECT MONTH(time) as month,
           COUNT(*) as total
    FROM earthquakes
    WHERE YEAR(time) = {}
    GROUP BY MONTH(time)
    ORDER BY month
    """.format(selected_year))

    fig_month = px.bar(df_month, x="month", y="total",
                       title="Earthquakes by Month")

    st.plotly_chart(fig_month, use_container_width=True)

# =====================================
# TAB 2 – MAGNITUDE & DEPTH
# =====================================

with tab2:

    st.subheader("Top 10 Strongest Earthquakes")

    df_top10 = load_data("""
    SELECT place, mag, depth_km
    FROM earthquakes
    ORDER BY mag DESC
    LIMIT 10
    """)

    st.dataframe(df_top10)

    st.subheader("Top 10 Deepest Earthquakes")

    df_deep = load_data("""
    SELECT place, depth_km, mag
    FROM earthquakes
    ORDER BY depth_km DESC
    LIMIT 10
    """)

    st.dataframe(df_deep)

    st.subheader("Magnitude Distribution")

    df_mag = load_data("""
    SELECT mag
    FROM earthquakes
    WHERE mag IS NOT NULL
    """)

    fig_mag = px.histogram(df_mag, x="mag",
                           nbins=40,
                           title="Magnitude Distribution")

    st.plotly_chart(fig_mag, use_container_width=True)

# =====================================
# TAB 3 – TSUNAMI & ALERTS
# =====================================

with tab3:

    st.subheader("Tsunami Events Per Year")

    df_tsunami = load_data("""
    SELECT YEAR(time) as year,
           COUNT(*) as tsunami_count
    FROM earthquakes
    WHERE tsunami = 1
    GROUP BY YEAR(time)
    ORDER BY year
    """)

    fig_tsunami = px.bar(df_tsunami,
                         x="year",
                         y="tsunami_count",
                         title="Tsunami Events")

    st.plotly_chart(fig_tsunami, use_container_width=True)

    st.subheader("Reviewed vs Automatic Status")

    df_status = load_data("""
    SELECT status,
           COUNT(*) as total
    FROM earthquakes
    GROUP BY status
    """)

    fig_status = px.pie(df_status,
                        names="status",
                        values="total",
                        title="Earthquake Status Distribution")

    st.plotly_chart(fig_status, use_container_width=True)

# =====================================
# TAB 4 – QUALITY METRICS
# =====================================

with tab4:

    st.subheader("Average RMS and GAP")

    df_quality = load_data("""
    SELECT AVG(rms) as avg_rms,
           AVG(gap) as avg_gap
    FROM earthquakes
    """)

    st.dataframe(df_quality)

    st.subheader("High Station Coverage (nst > 100)")

    df_nst = load_data("""
    SELECT place, nst, mag
    FROM earthquakes
    WHERE nst > 100
    ORDER BY nst DESC
    LIMIT 20
    """)

    st.dataframe(df_nst)

# =====================================
# MAP SECTION
# =====================================

st.subheader("🗺 Global Earthquake Map (Filtered by Magnitude)")

df_map = load_data(f"""
SELECT latitude, longitude, mag
FROM earthquakes
WHERE mag >= {min_mag}
""")

st.map(df_map)

# =====================================
# KEY INSIGHTS
# =====================================

st.divider()
st.subheader("📌 Key Insights")

st.write("""
• Earthquake frequency varies across years.
• Majority of events are moderate magnitude.
• Tsunami-triggering earthquakes are limited but significant.
• High station coverage improves reliability.
• Seismic activity clusters in specific geographic zones.
""")