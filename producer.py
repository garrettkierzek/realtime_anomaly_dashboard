
from kafka import KafkaProducer
import pandas as pd
import json
import time

# Load your synthetic dataset
df = pd.read_csv("synthetic_manufacturing_datasetV2.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.sort_values("timestamp").reset_index(drop=True)

# Optional: drop operator_note if not using it
df = df.drop(columns=["operator_note"])

# Ensure timestamp is string (Kafka-safe)
df["timestamp"] = pd.to_datetime(df["timestamp"]).astype(str)

# Set up Kafka producer
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

print("Kafka Producer started. Streaming records...\n")

# Loop through each row and send as a Kafka message
for idx, row in df.iterrows():
    message = row.to_dict()
    producer.send("machine_sensor_data", value=message)
    print(f"Sent record {idx + 1}: Machine {message['machine_id']} at {message['timestamp']}")
    time.sleep(3)  # stream timing

print("All records sent.")









































