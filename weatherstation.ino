#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// WiFi credentials
const char* ssid     = "kasrawy";
const char* password = "osama1234";

// HiveMQ credentials
const char* mqtt_server   = "08cd25878d7e4519991bd5bbbb73a2f7.s1.eu.hivemq.cloud";
const int   mqtt_port     = 8883;
const char* mqtt_user     = "weatherstation";
const char* mqtt_password = "Weather123";

// Sensor pins
#define DHTPIN 4
#define DHTTYPE DHT22
#define RAIN_AO 34
#define RAIN_DO 35
#define LDR_AO  33
#define LDR_DO  25
#define BUZZER  26
#define LED_GREEN 27
#define LED_RED   12

DHT dht(DHTPIN, DHTTYPE);
LiquidCrystal_I2C lcd(0x27, 16, 2);
WiFiClientSecure espClient;
PubSubClient client(espClient);

bool alertActive = false;

void handleAlert(String message) {
  message.trim(); // Remove any extra whitespace
  Serial.println("Alert message received: [" + message + "]");
  
  if (message == "ALL_CLEAR") {
    alertActive = false;
    digitalWrite(LED_GREEN, HIGH);
    digitalWrite(LED_RED, LOW);
    noTone(BUZZER);
  } else {
    alertActive = true;
    digitalWrite(LED_GREEN, LOW);
    digitalWrite(LED_RED, HIGH);
    tone(BUZZER, 1000, 200);
  }
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.print("Message received on topic: ");
  Serial.println(topic);
  Serial.println("Message: " + message);

  if (String(topic) == "weather/alert") {
    handleAlert(message);
  }
}

void connectWiFi() {
  Serial.print("Connecting to WiFi");
  WiFi.begin(ssid, password);
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Connecting WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected!");
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("WiFi Connected!");
  delay(1000);
}

void connectMQTT() {
  espClient.setInsecure();
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(mqttCallback);
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Connecting MQTT");
  while (!client.connected()) {
    Serial.print("Connecting to MQTT...");
    if (client.connect("ESP32Client", mqtt_user, mqtt_password)) {
      Serial.println("connected!");
      client.subscribe("weather/alert");
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("MQTT Connected!");
      delay(1000);
    } else {
      Serial.print("failed, rc=");
      Serial.println(client.state());
      delay(2000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  dht.begin();
  Wire.begin(21, 22);
  lcd.init();
  lcd.backlight();
  pinMode(RAIN_DO, INPUT);
  pinMode(LDR_DO, INPUT);
  pinMode(BUZZER, OUTPUT);
  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_RED, OUTPUT);

  // Startup sequence
  lcd.setCursor(0, 0);
  lcd.print("Weather Station");
  lcd.setCursor(0, 1);
  lcd.print("Starting...");
  digitalWrite(LED_GREEN, HIGH);
  digitalWrite(LED_RED, HIGH);
  tone(BUZZER, 1000, 500);
  delay(500);
  digitalWrite(LED_RED, LOW);

  connectWiFi();
  connectMQTT();
}

void loop() {
  if (!client.connected()) connectMQTT();
  client.loop();

  delay(500);

  float humidity    = dht.readHumidity();
  float temperature = dht.readTemperature();
  int   rainAnalog  = analogRead(RAIN_AO);
  int   ldrAnalog   = analogRead(LDR_AO);

  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("Failed to read from DHT22!");
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Sensor Error!");
    return;
  }

  // Publish to MQTT
  client.publish("weather/temperature", String(temperature).c_str());
  client.publish("weather/humidity",    String(humidity).c_str());
  client.publish("weather/rain",        String(rainAnalog).c_str());
  client.publish("weather/light",       String(ldrAnalog).c_str());

  // Local rain detection (only if no dashboard alert active)
  if (!alertActive) {
    if (rainAnalog < 2000) {
      digitalWrite(LED_GREEN, LOW);
      digitalWrite(LED_RED, HIGH);
      tone(BUZZER, 1000, 500);
    } else {
      digitalWrite(LED_GREEN, HIGH);
      digitalWrite(LED_RED, LOW);
      noTone(BUZZER);
    }
  }

  // LCD Display
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("T:");
  lcd.print(temperature, 1);
  lcd.print("C H:");
  lcd.print(humidity, 1);
  lcd.print("%");
  lcd.setCursor(0, 1);
  lcd.print("Rain:");
  lcd.print(rainAnalog < 2000 ? "YES" : "NO ");
  lcd.print(" L:");
  lcd.print(ldrAnalog);
}