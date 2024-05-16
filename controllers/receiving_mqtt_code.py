import json
from umqtt.simple import MQTTClient

# MQTT broker configuration
mqtt_broker = "your_broker_address"  # Update with your MQTT broker address
mqtt_port = 1883  # MQTT broker port
mqtt_user = "your_username"  # MQTT broker username (if applicable)
mqtt_password = "your_password"  # MQTT broker password (if applicable)
mqtt_client_id = "esp32"  # Client ID for MQTT connection
mqtt_topic = b"u47041165"  # MQTT topic to subscribe to

# Global variable to store received JSON data
received_data = None

def on_message(topic, message):
    """Callback function called when a message is received."""
    global received_data
    print(f"Received message on topic: {topic}")
    try:
        # Decode the message and load JSON data
        received_data = json.loads(message.decode("utf-8"))
        print("Received JSON data:", received_data)
        # Process the received data as needed
        # Insert your data processing logic here
    except Exception as e:
        print("Error processing JSON data:", e)

def setup():
    """Function to set up the MQTT client and subscribe to the topic."""
    global mqtt
    try:
        # Connect to MQTT broker
        mqtt = MQTTClient(client_id=mqtt_client_id,
                          server=mqtt_broker,
                          port=mqtt_port,
                          user=mqtt_user,
                          password=mqtt_password)
        mqtt.connect()
        print("Connected to MQTT broker")

        # Subscribe to the specified topic
        mqtt.set_callback(on_message)
        mqtt.subscribe(mqtt_topic)
        print(f"Subscribed to MQTT topic: {mqtt_topic.decode('utf-8')}")

    except Exception as e:
        print("Error during MQTT setup:", e)

def loop():
    """Function to continuously check for incoming MQTT messages."""
    try:
        # Check for new MQTT messages
        mqtt.check_msg()
        # Additional code can be added here for other tasks

    except Exception as e:
        print("Error in loop:", e)

# Setup MQTT connection and subscription
setup()

# Main loop to continuously process MQTT messages
while True:
    loop()
