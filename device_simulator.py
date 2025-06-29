# file: device_simulator.py
import paho.mqtt.client as mqtt
import json
import time
import ssl

# --- MQTT Settings ---
MQTT_BROKER_HOST = "ebdca87f8eb340cf96898aaee1fc1dae.s1.eu.hivemq.cloud"
MQTT_BROKER_PORT = 8883
MQTT_USERNAME = "Basilio"
MQTT_PASSWORD = "AirRoaster2011!"

# --- Test Configuration ---
# The topic must exactly match the topic you registered in the HMI
TARGET_TOPIC = "inventory/receive/platform_scale_100kg"

# The data payload to send.
# !! IMPORTANT !! Change "po_number" to match a real, "Pending" PO in your database.
TEST_PAYLOAD = {
    "po_number": "TEST-PO-001", 
    "new_lot_identifier": f"LOT-{int(time.time())}", # Creates a unique lot ID
    "weight_received_kg": 68.5
}

# --- Script Logic ---
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("Simulator connected successfully.")
        print(f"Publishing to topic: {TARGET_TOPIC}")
        print(f"Payload: {json.dumps(TEST_PAYLOAD)}")
        client.publish(TARGET_TOPIC, payload=json.dumps(TEST_PAYLOAD), qos=1)
    else:
        print(f"Simulator failed to connect, return code {rc}\n")

def on_publish(client, userdata, mid, reason_code, properties):
    print(f"Message Published with MID: {mid}. Disconnecting simulator.")
    client.disconnect()

# --- Main Execution ---
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"simulator_{int(time.time())}")
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
client.on_connect = on_connect
client.on_publish = on_publish

client.tls_set(tls_version=ssl.PROTOCOL_TLS)

print("--- Starting Device Simulator ---")
client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT)

client.loop_forever() # The loop will be stopped by the on_publish callback
print("--- Simulator Finished ---")