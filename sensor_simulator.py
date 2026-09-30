import json
import random
import time
import ssl
import paho.mqtt.client as mqtt

from config import BROKER, PORT, USERNAME, PASSWORD, TOPIC


client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id="compressed_air_sensor"
)

client.username_pw_set(USERNAME, PASSWORD)

client.tls_set(cert_reqs=ssl.CERT_REQUIRED)


def generate_sensor_data():

    # Normal operating condition
    pressure = random.uniform(6.5, 8.0)
    flow = random.uniform(35, 55)
    temperature = random.uniform(25, 35)
    power = random.uniform(4.0, 7.0)

    # Randomly create leakage event
    leak = random.random() < 0.15

    if leak:
        flow = random.uniform(70, 100)
        pressure = random.uniform(5.0, 6.3)
        power = random.uniform(7.0, 10.0)

    data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "pressure_bar": round(pressure, 2),
        "flow_lpm": round(flow, 2),
        "temperature_c": round(temperature, 2),
        "power_kw": round(power, 2)
    }

    return data


print("Connecting to HiveMQ...")

client.connect(BROKER, PORT)

print("Connected to HiveMQ")
print("Publishing sensor data...")
print("Topic:", TOPIC)

client.loop_start()


while True:

    data = generate_sensor_data()

    payload = json.dumps(data)

    client.publish(TOPIC, payload)

    print("Published:", data)

    time.sleep(2)