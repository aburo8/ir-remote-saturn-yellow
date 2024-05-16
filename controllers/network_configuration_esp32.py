import time
from umqtt.simple import MQTTClient
from machine import Pin
import network

# WiFi credentials
WIFI_SSID = "your_wifi_ssid"
WIFI_PASSWORD = "your_wifi_password"

# MQTT broker configuration
MQTT_BROKER = "mqtt_server_address"
MQTT_CLIENT_ID = "esp32_client"
MQTT_TOPIC_SUBSCRIBE = b"u47041165"
MQTT_TOPIC_PUBLISH = b"IR_topic"

# Define callback function for MQTT messages received
def mqtt_callback(topic, msg):
    print("Received message on topic: {}, message: {}".format(topic, msg))

# Connect to WiFi
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(WIFI_SSID, WIFI_PASSWORD)
while not wifi.isconnected():
    pass
print("WiFi connected:", wifi.ifconfig())

# Define MQTT client instance
client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER)

try:
    # Connect to MQTT broker
    client.connect()

    # Subscribe to MQTT topic
    client.subscribe(MQTT_TOPIC_SUBSCRIBE)

    # Main loop to wait for MQTT messages and publish periodically
    while True:
        # Check for incoming MQTT messages
        client.check_msg()

        # Publish a message periodically
        client.publish(MQTT_TOPIC_PUBLISH, b"Hello from ESP32")

        # Add a delay (e.g., 1 second) between publishes
        time.sleep(1)

except Exception as e:
    print("Error:", e)

finally:
    # Disconnect from MQTT broker
    try:
        client.disconnect()
    except:
        pass
