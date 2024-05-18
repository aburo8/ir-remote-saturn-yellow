#include <M5Core2.h>
#include <IRremote.hpp>

// Define the pin where your IR LED is connected
const int IR_LED_PIN = 19;

void setup() {
  // Initialize the M5Core2
  M5.begin();
  M5.Lcd.setTextSize(2);
  M5.Lcd.setTextColor(TFT_WHITE, TFT_BLACK);
  M5.Lcd.fillScreen(TFT_BLACK);

  // Initialize the IR transmitter
  //IrSender.begin(IR_LED_PIN, ENABLE_LED_FEEDBACK); // Begin with the specified pin and optional feedback LED
  IrSender.begin(IR_LED_PIN, ENABLE_LED_FEEDBACK, USE_DEFAULT_FEEDBACK_LED_PIN);
  // Display a message on the screen
  M5.Lcd.setCursor(10, 10);
  M5.Lcd.print("Ready to transmit");

  // Start the serial communication for debugging
  Serial.begin(115200);
}

void loop() {
  // Update the button status
  M5.update();
  
  // Wait for a button press to transmit the IR code
  if (M5.BtnA.wasPressed()) {
    // Transmit the IR code
    unsigned long irCode = 0xFB04EF00;
    uint16_t address = 0xEF00;
    uint16_t command = 0xFB04;


    //IrSender.sendNEC(irCode, 32); // NEC protocol, 32-bit code
    IrSender.sendNEC(address, command, 0);
    // Display the transmitted code on the screen
    M5.Lcd.fillScreen(TFT_BLACK);
    M5.Lcd.setCursor(10, 10);
    M5.Lcd.printf("Transmitted: %08X", irCode);
    
    // Print the transmitted code to the serial monitor
    Serial.print("Transmitted IR Code: ");
    Serial.println(irCode, HEX);
    
    // Wait for a short while before accepting another button press
    delay(1000);
  }
}