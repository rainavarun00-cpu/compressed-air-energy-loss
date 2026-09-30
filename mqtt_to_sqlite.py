import json
import sqlite3
import ssl
import os
import paho.mqtt.client as mqtt

from config import BROKER, PORT, USERNAME, PASSWORD, TOPIC, DATABASE


# Create data folder
os.makedirs("data", exist_ok=True)


# Connect SQLite
conn = sqlite3.connect(DATABASE, check_same_thread=False)

cursor = conn.cursor()


# Create table
cursor.execute("""
CREATE TABLE IF NOT EXISTS sensor_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    pressure_bar REAL,
    flow_lpm REAL,
    temperature_c REAL,
    power_kw REAL
)
""")

conn.commit()


def on_connect(client, userdata, flags, reason_code, properties):

    print("Connected to HiveMQ")

    client.subscribe(TOPIC)

    print("Subscribed to:", TOPIC)


def on_message(client, userdata, msg):

    try:

        data = json.loads(msg.payload.decode())

        cursor.execute("""
        INSERT INTO sensor_data
        (
            timestamp,
            pressure_bar,
            flow_lpm,
            temperature_c,
            power_kw
        )
        VALUES (?, ?, ?, ?, ?)
        """, (
            data["timestamp"],
            data["pressure_bar"],
            data["flow_lpm"],
            data["temperature_c"],
            data["power_kw"]
        ))

        conn.commit()

        print("Saved:", data)

    except Exception as e:

        print("Data error:", e)


client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id="sqlite_collector"
)

client.username_pw_set(USERNAME, PASSWORD)

client.tls_set(cert_reqs=ssl.CERT_REQUIRED)

client.on_connect = on_connect
client.on_message = on_message


print("Connecting to HiveMQ...")

client.connect(BROKER, PORT)

client.loop_forever()