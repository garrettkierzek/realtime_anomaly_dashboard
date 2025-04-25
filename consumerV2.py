from kafka import KafkaConsumer
from sklearn.ensemble import IsolationForest
import pandas as pd
import json
from openai import OpenAI
import os

# === OpenAI setup ===
api_key = os.getenv("api_key")
client = OpenAI(api_key=api_key)

# === Load training data ===
df = pd.read_csv("synthetic_manufacturing_datasetV2.csv")
df_normal = df[df["anomaly"] == 0]
feature_cols = ["temperature", "vibration", "pressure", "speed"]
X_train = df_normal[feature_cols]

iso = IsolationForest(contamination=0.0127, random_state=42)
iso.fit(X_train)

# === Kafka Consumer setup ===
consumer = KafkaConsumer(
    'machine_sensor_data',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='latest',
    enable_auto_commit=True,
    group_id='streamlit-group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

# === Stream folder setup ===
output_dir = r"D:\\BigDataAnalytics\\trendsmarketplace\\kafka_env\\stream_data"
os.makedirs(output_dir, exist_ok=True)
print(f"✅ Writing real-time data to {output_dir} ...")

# === Historical record storage ===
history_df = pd.DataFrame(columns=feature_cols + ["machine_id", "timestamp"])

def generate_explanation(record, history):
    # Get last 5 rows for this machine
    recent_history = history[history["machine_id"] == record["machine_id"]]
    recent_history = recent_history.sort_values("timestamp", ascending=False).head(5)

    trend_summary = "\n".join([
        f"{row['timestamp']}: Temp={row['temperature']:.1f}, Vib={row['vibration']:.2f}, Press={row['pressure']:.1f}, Speed={row['speed']:.0f}"
        for _, row in recent_history.iterrows()
    ])

    # Deviation from normal mean
    deltas = {
        "temperature": record["temperature"] - X_train["temperature"].mean(),
        "vibration": record["vibration"] - X_train["vibration"].mean(),
        "pressure": record["pressure"] - X_train["pressure"].mean(),
        "speed": record["speed"] - X_train["speed"].mean()
    }
    biggest_issue = max(deltas, key=lambda k: abs(deltas[k]))

    prompt = f"""
You are a senior technician overseeing a hydraulic stamping press used in producing automotive door panels. The machine uses high pressure and rapid movements to shape metal sheets with precision.

An anomaly was detected from Machine #{record['machine_id']} at {record['timestamp']}.

🔧 Sensor Readings:
- Temperature: {record['temperature']} °F
- Vibration: {record['vibration']} g
- Pressure: {record['pressure']} psi
- Speed: {record['speed']} RPM

📊 Deviations from baseline:
- Temperature deviation: {deltas['temperature']:.2f}
- Vibration deviation: {deltas['vibration']:.2f}
- Pressure deviation: {deltas['pressure']:.2f}
- Speed deviation: {deltas['speed']:.2f}

📈 Recent sensor trend (last 5 entries):
{trend_summary}

🛠️ The largest deviation was in **{biggest_issue}**.

Please:
1. Analyze the most likely mechanical or operational issue based on this data
2. Briefly explain what might be going wrong
3. Recommend what a technician should check first

Speak as if you're mentoring a junior technician — be clear, practical, and insightful.
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"(GPT error: {str(e)})"



# === Main loop ===
for msg in consumer:
    data = msg.value

    # anomaly detection
    try:
        x_row = pd.DataFrame([data])[feature_cols]
        anomaly_score = iso.decision_function(x_row)[0]
        is_anomaly = iso.predict(x_row)[0] == -1
    except Exception as e:
        print(f"Error processing record: {e}")
        continue

    # update historical records
    history_df = pd.concat([history_df, pd.DataFrame([data])]).tail(1000)

    # explanation
    suggestion = generate_explanation(data, history_df) if is_anomaly else "Normal operation."
    data['anomaly'] = int(is_anomaly)
    data['anomaly_score'] = round(anomaly_score, 4)
    data['suggestion'] = suggestion

    # file name
    timestamp = data['timestamp'].replace(":", "-").replace(" ", "_")
    file_name = os.path.join(output_dir, f"{timestamp}_machine{data['machine_id']}.json")

    # write
    try:
        with open(file_name, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Wrote file: {file_name}")
    except Exception as e:
        print(f"Error writing file: {e}")