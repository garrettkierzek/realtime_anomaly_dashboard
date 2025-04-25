import streamlit as st
import pandas as pd
import altair as alt
import os
import json
from streamlit_autorefresh import st_autorefresh

# === Page config ===
st.set_page_config(page_title="Real-time Machine Anomaly Dashboard", layout="wide")
st.title(" Real-time Machine Anomaly Dashboard")

# Auto-refresh every 3 seconds
st_autorefresh(interval=3000, key="stream-refresh")

# === Load JSON data from stream_data folder ===
data_path = "stream_data"

def load_latest_records(n=200):
    try:
        files = sorted(os.listdir(data_path), reverse=True)[:n]
        rows = []
        for f in files:
            with open(os.path.join(data_path, f)) as json_file:
                rows.append(json.load(json_file))
        return pd.DataFrame(rows)
    except Exception as e:
        st.error(f" Error loading stream_data files: {e}")
        return pd.DataFrame()

df = load_latest_records()

if df.empty:
    st.info("No data yet. Waiting for Kafka stream...")
    st.stop()

# === Data cleanup and prep ===
df["timestamp"] = pd.to_datetime(df["timestamp"])
df["machine_id"] = df["machine_id"].astype(str)
df.set_index("timestamp", inplace=True)

# === Header ===
st.markdown("<h1 style='text-align: center;'>Sensor Reading Dashboard</h1>", unsafe_allow_html=True)

# === Tables Section ===
st.subheader("Machine Overview")
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Faulty Machines")
    if "anomaly" in df.columns:
        faulty_df = df[df["anomaly"] == 1]
        if not faulty_df.empty:
            display_df = faulty_df.reset_index()[["timestamp", "machine_id", "temperature", "pressure", "speed", "vibration"]]
            st.dataframe(display_df.round(2), use_container_width=True)
        else:
            st.success("No faulty machines detected.")
    else:
        st.warning("Column 'anomaly' not found.")

with col2:
    st.markdown("#### Mean Sensor Readings (All Machines)")
    mean_df = df[["temperature", "pressure", "speed", "vibration"]].mean().to_frame().T.round(2)
    st.dataframe(mean_df, use_container_width=True)

# === Anomaly Explanation ===
st.markdown("<h3 style='text-align: center;'>Explanation for Anomalies</h3>", unsafe_allow_html=True)

if "anomaly" in df.columns and "suggestion" in df.columns:
    faulty_df = df[df["anomaly"] == 1]
    if not faulty_df.empty:
        machine_ids = faulty_df["machine_id"].unique().tolist()
        selected_machine = st.selectbox("Select a machine ID", machine_ids)

        explanation = (
            faulty_df[faulty_df["machine_id"] == selected_machine]
            .sort_values("timestamp", ascending=False)
            .iloc[0]["suggestion"]
        )

        st.markdown(f"""
        <div style='text-align: left; background-color: #f0f4ff; padding: 15px; border-radius: 8px;'>
            <strong>Machine {selected_machine}:</strong> {explanation}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.success("No anomalies to explain.")
else:
    st.warning("Missing 'anomaly' or 'suggestion' column.")

st.markdown("---")

# === Sensor Trends Section ===
st.subheader("Sensor Trends")

sensor_options = {
    "Temperature": "temperature",
    "Pressure": "pressure",
    "Speed": "speed",
    "Vibration": "vibration"
}

selected_label = st.selectbox("Select a sensor to view trend", list(sensor_options.keys()))
selected_sensor = sensor_options[selected_label]

# Machine filter
unique_machines = sorted(df["machine_id"].unique().tolist())
selected_machines = st.multiselect("Filter by Machine ID (optional)", unique_machines)

sensor_df = df.reset_index()[["timestamp", "machine_id", selected_sensor]].copy()
sensor_df[selected_sensor] = sensor_df[selected_sensor].round(2)

# === Show Average or Per-Machine Chart ===
if not selected_machines:
    avg_df = sensor_df.groupby("timestamp")[selected_sensor].mean().reset_index()
    avg_chart = alt.Chart(avg_df).mark_line(color="steelblue").encode(
        x=alt.X("timestamp:T", title="Time"),
        y=alt.Y(f"{selected_sensor}:Q", title=f"Average {selected_label}"),
        tooltip=[
            alt.Tooltip("timestamp:T", title="Time"),
            alt.Tooltip(f"{selected_sensor}:Q", title=f"Avg {selected_label}", format=".2f")
        ]
    ).properties(
        width=900,
        height=350,
        title=f"Average {selected_label} Trend Across All Machines"
    ).interactive()
    st.altair_chart(avg_chart, use_container_width=True)
else:
    filtered_df = sensor_df[sensor_df["machine_id"].isin(selected_machines)]
    if filtered_df.empty:
        st.warning("⚠️ No data found for selected machines.")
    else:
        chart = alt.Chart(filtered_df).mark_line().encode(
            x=alt.X("timestamp:T", title="Time"),
            y=alt.Y(f"{selected_sensor}:Q", title=selected_label),
            color=alt.Color("machine_id:N", title="Machine ID"),
            tooltip=[
                alt.Tooltip("timestamp:T", title="Time"),
                alt.Tooltip("machine_id:N", title="Machine"),
                alt.Tooltip(f"{selected_sensor}:Q", title=selected_label, format=".2f")
            ]
        ).properties(
            width=900,
            height=350,
            title=f"{selected_label} Trend by Machine"
        ).interactive()
        st.altair_chart(chart, use_container_width=True)
