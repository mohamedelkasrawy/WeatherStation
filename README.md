# 🌤️ Weather Forecast System
### ECE4302 – Advanced Networks | IoT Project | 2025/2026

A real-time IoT weather monitoring system that allows users to directly check live weather statistics online without the need of a weather forecasting agency. The system uses a collection of sensors to monitor weather and provide live reporting. Users can also set alerts for particular thresholds, and the system notifies them when weather parameters cross those values.

---

## 👥 Team Members
| Name | Registration |
|------|-------------|
| Mohamed Osama Elkasrawy | 231027849 |
| Youssef Mohamed Nabil | 231027793 |
| Youssef Islam | 231005146 |
| Mohamed Moataz | 231010054 |

---

## 🌐 Live Dashboard
👉 **[https://weatherstation-production-f287.up.railway.app](https://weatherstation-production-f287.up.railway.app)**

---

## 🏗️ System Architecture
The system consists of 3 main components:
- **Microcontroller (ESP32)** — reads sensor data and publishes via MQTT
- **Backend Server (Flask + MySQL)** — receives data, stores it, evaluates alerts, serves REST API
- **Web Dashboard (HTML/CSS/JS)** — displays live readings, historical charts, and alerts

---

## 📡 IoT Protocol — MQTT
**MQTT (Message Queuing Telemetry Transport)** was chosen because:
- Lightweight and efficient — perfect for IoT devices like ESP32
- Publish/Subscribe model enables real-time data delivery
- Supports WAN-scale communication over the internet
- Low bandwidth and low power consumption
- Supports TLS encryption on port 8883 for secure communication

**Broker:** HiveMQ Cloud (Free Tier)
**Port:** 8883 (TLS/SSL)

### MQTT Topics
| Topic | Description |
|-------|-------------|
| `weather/temperature` | Temperature in Celsius |
| `weather/humidity` | Humidity percentage |
| `weather/rain` | Rain analog level (0-4095) |
| `weather/light` | Light analog level (0-4095) |
| `weather/alert` | Alert messages from server to ESP32 |

---

## 🔧 Hardware Components
| Component | Pin | Purpose |
|-----------|-----|---------|
| ESP32 Dev Board | — | Main microcontroller with WiFi |
| DHT22 Sensor | GPIO 4 | Temperature & Humidity |
| Rain Sensor | GPIO 34 (AO), GPIO 35 (DO) | Rain detection |
| LDR Light Sensor | GPIO 33 (AO), GPIO 25 (DO) | Light intensity |
| 16x2 LCD (I2C) | GPIO 21 (SDA), GPIO 22 (SCL) | Local display |
| Buzzer | GPIO 26 | Audio alerts |
| Green LED | GPIO 27 | Normal status |
| Red LED | GPIO 12 | Alert status |

---

## 💻 Software Stack
| Layer | Technology |
|-------|-----------|
| Microcontroller | Arduino C++ (Arduino IDE) |
| IoT Protocol | MQTT via PubSubClient library |
| Backend | Python Flask |
| Database | MySQL (Railway Cloud) |
| Frontend | HTML, CSS, JavaScript, Chart.js |
| Deployment | Railway (Backend + DB), GitHub |

---

## 🗄️ Database Design
```sql
sensor_readings  (id, temperature, humidity, rain, light, timestamp)
alert_thresholds (id, parameter, min_value, max_value)
alert_logs       (id, parameter, value, message, timestamp)
```

---

## 🔌 REST API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/latest` | Latest sensor readings |
| GET | `/api/history` | Last 50 historical readings |
| GET | `/api/alerts` | Last 20 alert logs |
| GET | `/api/thresholds` | All alert thresholds |
| POST | `/api/thresholds` | Set new alert threshold |
| DELETE | `/api/thresholds/<id>` | Delete alert threshold |

---

## 🚀 How to Run Locally

### 1. Clone the repository
```bash
git clone https://github.com/mohamedelkasrawy/WeatherStation.git
cd WeatherStation
```

### 2. Install dependencies
```bash
pip install flask flask-cors paho-mqtt mysql-connector-python
```

### 3. Set up MySQL
```sql
CREATE DATABASE weather_db;
```

### 4. Run the server
```bash
python server.py
```

### 5. Upload ESP32 code
- Open `weatherstation.ino` in Arduino IDE
- Update WiFi credentials
- Upload to ESP32

---

## 📊 Features
- ✅ Live temperature, humidity, rain, and light monitoring
- ✅ Real-time web dashboard with charts
- ✅ User-defined alert thresholds
- ✅ Bidirectional MQTT communication
- ✅ Local alerts via buzzer and LEDs
- ✅ Historical data storage and visualization
- ✅ WAN accessible from anywhere in the world
- ✅ Secure MQTT over TLS

---

## 📁 Project Structure
WeatherStation/
├── server.py        # Flask backend server
├── index.html       # Web dashboard
├── requirements.txt # Python dependencies
└── README.md        # Project documentation
