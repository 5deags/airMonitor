
#include "WiFi.h"
#include "HTTPClient.h"
#include "Adafruit_CCS811.h"
#include "Adafruit_BMP280.h"
#include "ClosedCube_HDC1080.h"
#include "Wire.h"
#include "math.h"
#include "Adafruit_GFX.h"
#include "Adafruit_SSD1306.h"


// WIFI CONSTANTS
const char* ssid = "Cleo";
const char* password = "A2EF6FE599";
//const char* ssid = "KalameheCozy";
//const char* password = "Cozy1234";

// SENSORS
Adafruit_CCS811 ccs;
Adafruit_BMP280 bme;
ClosedCube_HDC1080 hdc1080;

// BOARD DATA
int board_ID = 1;

// DISPLAY RELATED
#define I2C_SDA 5
#define I2C_SCL 4
// W = WIDTH, H = HEIGHT
#define W 128
#define H 64

Adafruit_SSD1306 display(W, H, &Wire1, -1);




void setup() {
  Serial.begin(115200);
  Wire.begin();
  Wire1.begin(I2C_SDA, I2C_SCL, 115200);

  /////////////////////////////////////////////
  // Wifi start
  //

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.println("Connecting to the WiFi network ...");
  }

  Serial.println("Connection established");

  /////////////////////////////////////////////

  /////////////////////////////////////////////
  // Sensor start-up

  // CCS sensor I2C 0x5A
  if(!ccs.begin(0x5A)) {
    Serial.println("Failed to start CCS811 sensor. Check connections/wiring.");
    while(1);
  }

  Serial.println("CCS811 sensor online.");
  
  float temp = ccs.calculateTemperature();
  ccs.setTempOffset(temp - 45.0);


  // BMP sensor I2C addr 0x76
  if (!bme.begin(0x76)) {
    Serial.println("Failed to start BMP280 sensor. Check connections/wiring.");
    while (1);
  }

  Serial.println("BMP280 sensor online.");

  // HDC1080 sensor I2C addr 0x40
  hdc1080.begin(0x40);

  Serial.println("HDC1080 sensor online.");

  /////////////////////////////////////////////


  /////////////////////////////////////////////
  // Display startup

  display.begin(SSD1306_SWITCHCAPVCC, 0x3c);
  display.clearDisplay();
  display.setTextColor(WHITE);
  display.setTextSize(1);

  Serial.println("Display online.");

  // Delay so that all sensors start getting correct and calibrated readings and so that the display would start up
  // Should be 3-4 in the final cut
  Serial.println("Calibrating sensors...");
  // CCS calibration reading
  ccs.readData();
  (ccs.calculateTemperature() - 32) * 5/9;
  ccs.getTVOC();
  ccs.geteCO2();

  // BMP calibration reading
  bme.readPressure()/1000;
  bme.readTemperature();

  // HDC calibration reading
  hdc1080.readHumidity();
  hdc1080.readTemperature();

  delay(6000);
  ccs.getTVOC();
  ccs.geteCO2();
  
  Serial.println("Calibration done.");

}

void post(float temp, float pressure, float VOC, float CO2, float humidity) {
  HTTPClient http;

  http.begin("https://airmonitor-2020.herokuapp.com/data");
  http.addHeader("Content-Type", "text/plain");

  int httpResponseCode = http.POST(String(board_ID) + "," + String(temp) + "," + String(pressure) + "," + String(VOC) +
  "," + String(CO2) + "," + String(humidity));

  if(httpResponseCode>0) {
    String response = http.getString();
    Serial.println(httpResponseCode);
    Serial.println(response);
  }
  else {
    Serial.print("Error on sending POST request: ");
    Serial.println(httpResponseCode);
  }

  http.end();
  
}

int rateAirQuality(float temp, float VOC, float CO2, float humidity) {
  // EACH OF THE 4 CATEGORIES GIVE 25 POINTS.
  // 25 IS MAX, 0 is MIN that a category can give
  // VOC LIMITS
  // 108 ppb VOC is WORST
  // 1 is BEST

  // CO2 LIMITS
  // 5000 WORST
  // 350 GOOD

  // HUMIDITY
  // HAS TO BE BELOW 60%, 60+% is WORST
  // 50%-59.99% is average
  // Below 50% is good

  // TEMPERATURE
  // 20-26 is good
  // UNDER 18 is bad and over 28 is bad
  int VOC_rating;
  int CO2_rating;
  int temp_rating;
  int hum_rating;

  // VOC RATING CALCULATION
  if (VOC > 108.0) {
    VOC_rating = 0;
  }
  else if (VOC <= 1.0) {
    VOC_rating = 25;
  }
  else {
    VOC_rating = (int) round(25-(25*((VOC-1.0)/107.0)));
  }
  Serial.println("VOC_rating: " + String(VOC_rating));
  
  // CO2 RATING CALCULATION
  if (CO2 > 5000.0) {
    CO2_rating = 0;
  }
  else if (CO2 <= 350.0) {
    CO2_rating = 25;
  }
  else {
    CO2_rating = (int) round(25-(25*((CO2-350.0)/4650.0)));
  }
  Serial.println("CO2_rating: " + String(CO2_rating));

  // HUMIDITY RATING CALCULATION
  if (humidity > 60.0) {
    hum_rating = 0;
  }
  else if (humidity <= 50.0) {
    hum_rating = 25;
  }
  else {
    hum_rating = (int) round(25-(25*((humidity-50.0)/10.0)));
  }
  Serial.println("hum_rating: " + String(hum_rating));

  // TEMP RATING CALCULATION
  if (temp > 28.0 || temp < 18.0) {
    temp_rating = 0;
  }
  else if (temp <= 26.0 && temp >= 20.0 ) {
    temp_rating = 25;
  }
  else {
    // Ülemine limiit ehk kalkulatsioonis kasutame 26 best ja 28 worst
    if (temp > 23) {
      temp_rating = (int) round(25-(25*((fabs(temp-26.0))/2.0)));
    }
    // Alumine limiit ehk kalkulatsioonis kasutame 20 best ja 18 worst
    else {
      temp_rating = (int) round(25-(25*((fabs(temp-20.0))/2.0)));
    }
  }
  Serial.println("temp_rating: " + String(temp_rating));

  
  return (VOC_rating + CO2_rating + temp_rating + hum_rating);
}

void displayData(int rating, String stringRating, float temp, float pressure,
float VOC, float CO2, float humidity) {
  display.clearDisplay();
  // X, Y
  // AIR QUALITY RATING
  display.setCursor(0,0);
  display.print("Air Quality Rating");

  // LEFT COLUMN
  display.setCursor(0, 10);
  display.print(String(rating) + "/100");

  // RIGHT COLUMN
  display.setCursor(60, 10);
  display.print(String(stringRating));

  // CURRENT SHOWINGS
  display.setCursor(0, 20);
  display.print("Current readings");

  // LEFT COLUMN
  display.setCursor(0, 30);
  display.print(String(temp) + " C");
  display.setCursor(0, 40);
  display.print(String(pressure) + " bar");
  display.setCursor(0, 50);
  display.print(String(VOC) + " ppb");

  // RIGHT COLUMN
  display.setCursor(50, 30);
  display.print(String(CO2) + " ppm");
  display.setCursor(80, 50);
  display.print(String(humidity) + "%");
  
  display.display();
}

// LOOP SHOULD HAVE 3-5 min DELAY IN THE BEGGINING BECAUSE VOC AND CO2 DATA TAKES LONGER TO COLLECT
void loop() {
  // Getting data from sensor
  float CCStemp;          // F
  float CCSVOC;           // ppb
  float CCSCO2;           // ppm

  // BMP data
  float BMPpressure;      // bar
  float BMPtemp;          // C

  // HDC1080 data
  float HDChumidity;      // %
  float HDCtemp;;         // C

  // TEMP AVERAGE BASED ON 3 SENSORS
  float TEMPavg;
  
  
  if(ccs.available()){
    ccs.readData();
    // CCS data
    CCStemp = (ccs.calculateTemperature() - 32) * 5/9; // C
    CCSVOC = ccs.getTVOC();               // ppb
    CCSCO2 = ccs.geteCO2();               // ppm

    // BMP data
    BMPpressure = bme.readPressure()/1000;// bar
    BMPtemp = bme.readTemperature();      // C

    // HDC1080 data
    HDChumidity = hdc1080.readHumidity(); // %
    HDCtemp = hdc1080.readTemperature();  // C

    // TEMP AVERAGE BASED ON 2 SENSORS

    //TEMPavg = (BMPtemp + HDCtemp)/2 - 5;
    TEMPavg = BMPtemp - 5;
    
    
    // %
    Serial.println("HDC Humidity: " + String(HDChumidity) + "%");
    // Celsius
    Serial.println("HDC Temperature: " + String(HDCtemp) + " C");
    // Original: Hectopascal | Modified to: bar
    Serial.println("BMP pressure: " + String(BMPpressure) + " bar");
    Serial.println("BMP temperature: " + String(BMPtemp) + " C");
    Serial.println("CCS881 CO2: " + String(CCSCO2) + " ppm");
    Serial.println("CCS881 VOC: " + String(CCSVOC) + " ppb");
    Serial.println("CCS881 Temperature: " + String(CCStemp) + " C");
    Serial.println("3 sensor temp avg: " + String(TEMPavg) + " C");
  }
  
  
  ///////////////////////////////////////////////////////////////
  // GETTING AND DISPLAYING AIR QUALITY RATINGS
  // GET AIR QUALITY RATING
  int rating = rateAirQuality(TEMPavg, CCSVOC, CCSCO2, HDChumidity);
  // DISPLAY AIR QUALITY RAITING ON OLED SCREEN
  String stringRating;
  if (rating < 50) {
    // BAD
    stringRating = "BAD";
  } else if (rating < 75) {
    // AVERAGE
    stringRating = "AVERAGE";
  } else {
    // GOOD
    stringRating = "GOOD";
  }

  displayData(rating, stringRating, TEMPavg, BMPpressure, CCSVOC, CCSCO2, HDChumidity);
  Serial.println("------------------------------------------------------");
  ///////////////////////////////////////////////////////////////
  
  
  
  // POST REQUEST
  post(TEMPavg, BMPpressure, CCSVOC, CCSCO2, HDChumidity);
  // Delay is in ms 60000 ms = 1 minute
  // 900000 ms = 15 min
  delay(300000);
}
