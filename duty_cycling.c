/*
Simple Deep Sleep with Timer Wake Up
=====================================
ESP32 offers a deep sleep mode for effective power
saving as power is an important factor for IoT
applications. In this mode CPUs, most of the RAM,
and all the digital peripherals which are clocked
from APB_CLK are powered off. The only parts of
the chip which can still be powered on are:
RTC controller, RTC peripherals ,and RTC memories

This code displays the most basic deep sleep with
a timer to wake it up and how to store data in
RTC memory to use it over reboots

This code is under Public Domain License.

Author:
Pranav Cherukupalli <cherukupallip@gmail.com>
*/

#include <Wire.h>
#include <Adafruit_TSL2591.h>

// Create sensor instances
Adafruit_TSL2591 tsl = Adafruit_TSL2591(2591);

#define PH_SENSOR_PIN 0  // GPIO 0 connected to the sensor's analog output
#define SOIL_MOISTURE_PIN 1  // GPIO 1 connected to the sensor's analog output

#define uS_TO_S_FACTOR 1000000  /* Conversion factor for micro seconds to seconds */
#define TIME_TO_SLEEP  5        /* Time ESP32 will go to sleep (in seconds) */

RTC_DATA_ATTR int bootCount = 0;

void configureSensor() {
  // Set gain and integration time for the TSL2591
  tsl.setGain(TSL2591_GAIN_MED);        // Options: LOW, MED, HIGH, MAX
  tsl.setTiming(TSL2591_INTEGRATIONTIME_100MS); // Options: 100MS, 200MS, 300MS, 400MS, 500MS, 600MS
}

/*
Method to print the reason by which ESP32
has been awaken from sleep
*/
void print_wakeup_reason(){
  esp_sleep_wakeup_cause_t wakeup_reason;

  wakeup_reason = esp_sleep_get_wakeup_cause();

  switch(wakeup_reason)
  {
    case ESP_SLEEP_WAKEUP_EXT0 : Serial.println("Wakeup caused by external signal using RTC_IO"); break;
    case ESP_SLEEP_WAKEUP_EXT1 : Serial.println("Wakeup caused by external signal using RTC_CNTL"); break;
    case ESP_SLEEP_WAKEUP_TIMER : Serial.println("Wakeup caused by timer"); break;
    case ESP_SLEEP_WAKEUP_TOUCHPAD : Serial.println("Wakeup caused by touchpad"); break;
    case ESP_SLEEP_WAKEUP_ULP : Serial.println("Wakeup caused by ULP program"); break;
    default : Serial.printf("Wakeup was not caused by deep sleep: %d\n",wakeup_reason); break;
  }
}

void setup(){
  Serial.begin(115200);
  delay(1000); //Take some time to open up the Serial Monitor

  //Increment boot number and print it every reboot
  ++bootCount;
  Serial.println("Boot number: " + String(bootCount));

  //Print the wakeup reason for ESP32
  print_wakeup_reason();

  /*
  First we configure the wake up source
  We set our ESP32 to wake up every 5 seconds
  */
  esp_sleep_enable_timer_wakeup(TIME_TO_SLEEP * uS_TO_S_FACTOR);
  Serial.println("Setup ESP32 to sleep for every " + String(TIME_TO_SLEEP) +
  " Seconds");

  while (!Serial);
  
  // Initialize I2C GPIO 8 (SCL) and GPIO 9 (SDA)
  Wire.begin(9, 8);

    // Get full-spectrum (visible + IR) and IR-only light levels
  uint32_t full = tsl.getFullLuminosity();
  uint16_t visible = full & 0xFFFF;
  uint16_t infrared = full >> 16;

  // Calculate Lux from the sensor readings
  float lux = tsl.calculateLux(visible, infrared);

  // Print TSL2591 readings
  Serial.print(F("Visible Light: ")); Serial.print(visible);
  Serial.print(F(" | Infrared: ")); Serial.print(infrared);
  Serial.print(F(" | Lux: ")); Serial.println(lux);

  // Read the raw ADC value from the pH sensor
  int raw_ADC_value = analogRead(PH_SENSOR_PIN);

  // Convert raw value to voltage (ESP32 ADC resolution is 12-bit by default)
  float voltage = (raw_ADC_value / 4095.0) * 3.3;

  // Convert the voltage to pH value using calibration
  float pH = 3.5 * voltage;  // Adjust the multiplier and offset as needed

  // Print pH readings
  Serial.print("Raw ADC Value: ");
  Serial.print(raw_ADC_value);
  Serial.print(" | Voltage: ");
  Serial.print(voltage, 2);
  Serial.print(" V | pH: ");
  Serial.println(pH, 2);

  // Read the raw analog value from the sensor
  int raw_value = analogRead(SOIL_MOISTURE_PIN);

  // Convert the raw value to a percentage (assuming 0-100%)
  // Calibration: You may need to determine the min (dry) and max (wet) raw values for your sensor
  float min_raw = 0;   // Replace with your dry calibration value
  float max_raw = 4095; // Replace with your wet calibration value (for ESP32 ADC resolution)

  // Map the raw value to a percentage
  float moisture_percent = map(raw_value, min_raw, max_raw, 0, 100);
  moisture_percent = constrain(moisture_percent, 0, 100); // Ensure the value stays within 0-100%

  // Print the readings to the Serial Monitor
  Serial.print("Raw ADC Value: ");
  Serial.print(raw_value);
  Serial.print(" | Soil Moisture: ");
  Serial.print(moisture_percent, 1);  // Print moisture percentage with 1 decimal place
  Serial.println("%");

  /*
  Next we decide what all peripherals to shut down/keep on
  By default, ESP32 will automatically power down the peripherals
  not needed by the wakeup source, but if you want to be a poweruser
  this is for you. Read in detail at the API docs
  http://esp-idf.readthedocs.io/en/latest/api-reference/system/deep_sleep.html
  Left the line commented as an example of how to configure peripherals.
  The line below turns off all RTC peripherals in deep sleep.
  */
  //esp_deep_sleep_pd_config(ESP_PD_DOMAIN_RTC_PERIPH, ESP_PD_OPTION_OFF);
  //Serial.println("Configured all RTC Peripherals to be powered down in sleep");

  /*
  Now that we have setup a wake cause and if needed setup the
  peripherals state in deep sleep, we can now start going to
  deep sleep.
  In the case that no wake up sources were provided but deep
  sleep was started, it will sleep forever unless hardware
  reset occurs.
  */
  Serial.println("Going to sleep now");
  delay(1000);
  Serial.flush(); 
  esp_deep_sleep_start();
  Serial.println("This will never be printed");
}

void loop(){
  //This is not going to be called
}
