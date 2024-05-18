#include <M5Core2.h>
#include <IRremote.hpp>
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// Define the pin where your IR LED is connected
const int IR_LED_PIN = 19;

// WiFi credentials
const char* ssid = "AB-DEV";
const char* password = "AB_d3V@2024";

// MQTT Broker credentials
const char* mqtt_server = "192.168.1.21";
const char* mqtt_username = "controller";
const char* mqtt_password = "csse4011";

// MQTT client
WiFiClient espClient;
PubSubClient client(espClient);

// Function prototypes
void setup_wifi();
void callback(char* topic, byte* message, unsigned int length);
void reconnect();

void setup() {
  // Initialize the M5Core2
  M5.begin();
  M5.Lcd.setTextSize(2);
  M5.Lcd.setTextColor(TFT_WHITE, TFT_BLACK);
  M5.Lcd.fillScreen(TFT_BLACK);

  // Initialize the IR transmitter
  IrSender.begin(IR_LED_PIN, ENABLE_LED_FEEDBACK, USE_DEFAULT_FEEDBACK_LED_PIN);

  // Start the serial communication for debugging
  Serial.begin(115200);

  // Initialize WiFi and MQTT
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
  
  // Display a message on the screen
  M5.Lcd.setCursor(10, 10);
  M5.Lcd.print("Ready to transmit");
}

void loop() {
  // Update the button status
  M5.update();
  
  // Ensure MQTT connection
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
}

// Connect to WiFi
void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

// MQTT callback function
void callback(char* topic, byte* message, unsigned int length) {
  Serial.print("Message arrived on topic: ");
  Serial.print(topic);
  Serial.print(". Message: ");
  String messageTemp;
  
  for (unsigned int i = 0; i < length; i++) {
    messageTemp += (char)message[i];
  }
  Serial.println(messageTemp);

  // Parse the JSON message
  StaticJsonDocument<200> doc;
  DeserializationError error = deserializeJson(doc, messageTemp);
  if (error) {
    Serial.print("Failed to parse JSON: ");
    Serial.println(error.c_str());
    return;
  }

  unsigned long irCode = doc["IR"];
  
  // Transmit the IR code
  uint16_t command = (irCode >> 16) & 0xFFFF;
  uint16_t address = irCode & 0xFFFF;
  IrSender.sendNEC(address, command, 0);

  // Display the transmitted code on the screen
  M5.Lcd.fillScreen(TFT_BLACK);
  M5.Lcd.setCursor(10, 10);
  M5.Lcd.printf("Transmitted: %08X", irCode);
  
  // Print the transmitted code to the serial monitor
  Serial.print("Transmitted IR Code: ");
  Serial.println(irCode, HEX);
}

// Reconnect to MQTT broker
void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect with username and password
    if (client.connect("M5Core2Client", mqtt_username, mqtt_password)) {
      Serial.println("connected");
      // Subscribe to the topic
      client.subscribe("topic/ir");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}