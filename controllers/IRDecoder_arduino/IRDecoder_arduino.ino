#include <M5Core2.h>
#include <IRremote.h>

int IRPIN = 26;

void setup() {
  Serial.begin(115200); // Start the serial communication for debugging
  Serial.println("Enabling IRin");

  IrReceiver.begin(IRPIN, ENABLE_LED_FEEDBACK);

  Serial.println("Enabled IRin");

  // Initialize the M5Core2
  M5.begin();
  M5.Lcd.setTextSize(2);
  M5.Lcd.setTextColor(TFT_WHITE, TFT_BLACK);
  M5.Lcd.fillScreen(TFT_BLACK);
  // Display a message on the screen
  M5.Lcd.setCursor(10, 10);
  M5.Lcd.print("Ready to receive");
}

void loop() {
  if (IrReceiver.decode()) {
    // Get the raw data
    uint32_t rawData = IrReceiver.decodedIRData.decodedRawData;
    
    // Decode the protocol
    const char* protocol = "UNKNOWN";
    switch (IrReceiver.decodedIRData.protocol) {
      case NEC:
        protocol = "NEC";
        break;
      case SONY:
        protocol = "SONY";
        break;
      case RC5:
        protocol = "RC5";
        break;
      case RC6:
        protocol = "RC6";
        break;
      case SHARP:
        protocol = "SHARP";
        break;
      case JVC:
        protocol = "JVC";
        break;
      case SAMSUNG:
        protocol = "SAMSUNG";
        break;
      case WHYNTER:
        protocol = "WHYNTER";
        break;
      case LG:
        protocol = "LG";
        break;
      case PANASONIC:
        protocol = "PANASONIC";
        break;
      case DENON:
        protocol = "DENON";
        break;
      default:
        protocol = "UNKNOWN";
        break;
    }

    // Print the decoded information to the serial monitor
    Serial.print("Protocol: ");
    Serial.print(protocol);
    Serial.print(", Raw Data: ");
    Serial.println(rawData, HEX);

    // Display the transmitted code and protocol on the screen
    M5.Lcd.fillScreen(TFT_BLACK);
    M5.Lcd.setCursor(10, 10);
    M5.Lcd.printf("Protocol: %s", protocol);
    M5.Lcd.setCursor(10, 30);
    M5.Lcd.printf("Raw Data: %08X", rawData);

    IrReceiver.resume(); // Receive the next value
  }

  delay(500);
}