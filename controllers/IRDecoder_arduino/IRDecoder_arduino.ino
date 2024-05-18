#include <M5Core2.h>
#include <IRremote.h>

int IRPIN = 26;

void setup()

{
Serial.println("Enabling IRin");

IrReceiver.begin(IRPIN, ENABLE_LED_FEEDBACK);

Serial.println("Enabled IRin");

M5.begin();
M5.Lcd.setTextSize(2);
M5.Lcd.setTextColor(TFT_WHITE, TFT_BLACK);
M5.Lcd.fillScreen(TFT_BLACK);
// Display a message on the screen
M5.Lcd.setCursor(10, 10);
M5.Lcd.print("Ready to recieve");

// Start the serial communication for debugging
Serial.begin(115200);

}

void loop()

{

if (IrReceiver.decode())

{

Serial.println(IrReceiver.decodedIRData.decodedRawData, HEX);
// Display the transmitted code on the screen
M5.Lcd.fillScreen(TFT_BLACK);
M5.Lcd.setCursor(10, 10);
M5.Lcd.printf("Transmitted: %08X", IrReceiver.decodedIRData.decodedRawData);
//M5.Lcd.printf("Protocol: %s\n", decode_type_str(results.decode_type));
//M5.Lcd.printf("IR Code: 0x%08X", IrReceiver.decodedIRData.decodedRawData);
IrReceiver.resume();

}

delay(500);

}