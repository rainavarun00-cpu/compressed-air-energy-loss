import sqlite3
import time
import os

import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import joblib


# ==========================================
# CONFIGURATION
# ==========================================

DATABASE = "data/sensor_data.db"
MODEL = "air_leak_model.pkl"

st.set_page_config(
    page_title="Compressed Air Energy Loss Detection",
    page_icon="💨",
    layout="wide"
)


# ==========================================
# TITLE
# ==========================================

st.title("💨 Compressed-Air Energy Loss Detection System")

st.caption(
    "MQTT → HiveMQ → SQLite → AI/ML → Dashboard → Alert"
)


# ==========================================
# LOAD DATABASE
# ==========================================

def load_data():

    if not os.path.exists(DATABASE):
        return pd.DataFrame()

    try:

        conn = sqlite3.connect(
            DATABASE,
            timeout=10
        )

        df = pd.read_sql_query(
            """
            SELECT *
            FROM sensor_data
            ORDER BY id DESC
            LIMIT 100
            """,
            conn
        )

        conn.close()

        if not df.empty:
            df = df.sort_values("id")

        return df

    except Exception as e:

        st.error(f"Database error: {e}")

        return pd.DataFrame()


df = load_data()


# ==========================================
# CHECK DATA
# ==========================================

if df.empty:

    st.warning(
        "⚠️ No sensor data available."
    )

    st.info(
        "Make sure HiveMQ/MQTT is running and "
        "mqtt_to_sqlite.py is inserting data into SQLite."
    )

    st.stop()


# ==========================================
# CHECK REQUIRED COLUMNS
# ==========================================

required_columns = [
    "timestamp",
    "pressure_bar",
    "flow_lpm",
    "temperature_c",
    "power_kw"
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:

    st.error(
        f"Missing database columns: {missing_columns}"
    )

    st.stop()


# ==========================================
# CONVERT DATA TYPES
# ==========================================

numeric_columns = [
    "pressure_bar",
    "flow_lpm",
    "temperature_c",
    "power_kw"
]

for column in numeric_columns:

    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )

df = df.dropna(
    subset=numeric_columns
)


# ==========================================
# AI DETECTION
# ==========================================

status = "UNKNOWN"
score = 0

if os.path.exists(MODEL):

    try:

        model = joblib.load(MODEL)

        features = [
            "pressure_bar",
            "flow_lpm",
            "temperature_c",
            "power_kw"
        ]

        X = df[features]

        predictions = model.predict(X)

        # Some ML models may not have decision_function
        if hasattr(model, "decision_function"):

            scores = model.decision_function(X)

        else:

            scores = [0] * len(df)

        latest_prediction = predictions[-1]

        latest_score = scores[-1]

        score = round(
            float(latest_score),
            4
        )

        if latest_prediction == -1:

            status = "POSSIBLE AIR LEAK"

        else:

            status = "NORMAL"

    except Exception as e:

        st.warning(
            f"AI model error: {e}"
        )

else:

    st.warning(
        "⚠️ AI model file not found: air_leak_model.pkl"
    )


# ==========================================
# LATEST VALUES
# ==========================================

latest = df.iloc[-1]


col1, col2, col3, col4, col5 = st.columns(5)


col1.metric(
    "Pressure",
    f"{latest['pressure_bar']:.2f} bar"
)


col2.metric(
    "Air Flow",
    f"{latest['flow_lpm']:.2f} L/min"
)


col3.metric(
    "Temperature",
    f"{latest['temperature_c']:.2f} °C"
)


col4.metric(
    "Power",
    f"{latest['power_kw']:.2f} kW"
)


col5.metric(
    "AI Status",
    status
)


st.divider()


# ==========================================
# AI SCORE
# ==========================================

st.subheader("🤖 AI Analysis")

st.metric(
    "Anomaly Score",
    score
)


# ==========================================
# ALERT
# ==========================================

if status == "POSSIBLE AIR LEAK":

    st.error(
        "🚨 ALERT: Possible compressed-air leakage detected!"
    )

else:

    st.success(
        "✅ System operating normally."
    )


# ==========================================
# PRESSURE CHART
# ==========================================

st.subheader("📊 Pressure")

fig_pressure = go.Figure()


fig_pressure.add_trace(
    go.Scatter(
        x=df["timestamp"],
        y=df["pressure_bar"],
        mode="lines+markers",
        name="Pressure"
    )
)


fig_pressure.update_layout(
    xaxis_title="Time",
    yaxis_title="Pressure (bar)"
)


st.plotly_chart(
    fig_pressure,
    use_container_width=True
)


# ==========================================
# AIR FLOW CHART
# ==========================================

st.subheader("📊 Air Flow")

fig_flow = go.Figure()


fig_flow.add_trace(
    go.Scatter(
        x=df["timestamp"],
        y=df["flow_lpm"],
        mode="lines+markers",
        name="Air Flow"
    )
)


fig_flow.update_layout(
    xaxis_title="Time",
    yaxis_title="Flow (L/min)"
)


st.plotly_chart(
    fig_flow,
    use_container_width=True
)


# ==========================================
# TEMPERATURE / POWER
# ==========================================

col1, col2 = st.columns(2)


# ------------------------------------------
# TEMPERATURE
# ------------------------------------------

with col1:

    st.subheader("🌡️ Temperature")

    fig_temp = go.Figure()


    fig_temp.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=df["temperature_c"],
            mode="lines",
            name="Temperature"
        )
    )


    fig_temp.update_layout(
        xaxis_title="Time",
        yaxis_title="Temperature (°C)"
    )


    st.plotly_chart(
        fig_temp,
        use_container_width=True
    )


# ------------------------------------------
# POWER
# ------------------------------------------

with col2:

    st.subheader("⚡ Power Consumption")

    fig_power = go.Figure()


    fig_power.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=df["power_kw"],
            mode="lines",
            name="Power"
        )
    )


    fig_power.update_layout(
        xaxis_title="Time",
        yaxis_title="Power (kW)"
    )


    st.plotly_chart(
        fig_power,
        use_container_width=True
    )


# ==========================================
# LIVE DATA TABLE
# ==========================================

st.subheader("📡 Latest Sensor Data")

st.dataframe(
    df.tail(20),
    use_container_width=True
)


# ==========================================
# SYSTEM INFORMATION
# ==========================================

st.subheader("🔗 System Information")

info1, info2, info3 = st.columns(3)


info1.metric(
    "Database",
    "SQLite"
)


info2.metric(
    "Data Source",
    "HiveMQ / MQTT"
)


info3.metric(
    "AI Model",
    "Air Leak Detection"
)


# ==========================================
# AUTO REFRESH
# ==========================================

time.sleep(2)

st.rerun()