from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import paho.mqtt.client as mqtt
import mysql.connector
import threading
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

# MySQL config
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'admin123',
    'database': 'weather_db'
}

# HiveMQ config
MQTT_BROKER   = "08cd25878d7e4519991bd5bbbb73a2f7.s1.eu.hivemq.cloud"
MQTT_PORT     = 8883
MQTT_USER     = "weatherstation"
MQTT_PASSWORD = "Weather123"

# Latest sensor data
latest_data = {
    "temperature": 0,
    "humidity": 0,
    "rain": 0,
    "light": 0,
    "timestamp": ""
}

def get_db():
    return mysql.connector.connect(**db_config)

def on_connect(client, userdata, flags, rc, properties=None):
    print("Connected to MQTT broker!")
    client.subscribe("weather/#")

def on_message(client, userdata, msg):
    topic = msg.topic
    value = msg.payload.decode()
    print(f"Received: {topic} = {value}")

    parameter = topic.split("/")[1]
    latest_data[parameter] = float(value)
    latest_data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Save to database every time all 4 readings are received
    if all(latest_data[k] != 0 for k in ["temperature", "humidity"]):
        save_to_db()
        check_alerts()

def save_to_db():
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO sensor_readings (temperature, humidity, rain, light)
            VALUES (%s, %s, %s, %s)
        """, (
            latest_data["temperature"],
            latest_data["humidity"],
            latest_data["rain"],
            latest_data["light"]
        ))
        db.commit()
        cursor.close()
        db.close()
        print("Data saved to database!")
    except Exception as e:
        print(f"Database error: {e}")

def check_alerts():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM alert_thresholds")
        thresholds = cursor.fetchall()
        for threshold in thresholds:
            param = threshold["parameter"]
            value = latest_data.get(param, 0)
            if value < threshold["min_value"] or value > threshold["max_value"]:
                message = f"{param} is {value} which is out of range!"
                cursor.execute("""
                    INSERT INTO alert_logs (parameter, value, message)
                    VALUES (%s, %s, %s)
                """, (param, value, message))
                db.commit()
                print(f"ALERT: {message}")
        cursor.close()
        db.close()
    except Exception as e:
        print(f"Alert error: {e}")

# MQTT setup
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
mqtt_client.tls_set()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

def start_mqtt():
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_forever()

mqtt_thread = threading.Thread(target=start_mqtt)
mqtt_thread.daemon = True
mqtt_thread.start()

# API Routes
@app.route("/api/latest", methods=["GET"])
def get_latest():
    return jsonify(latest_data)

@app.route("/api/history", methods=["GET"])
def get_history():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM sensor_readings ORDER BY timestamp DESC LIMIT 50")
        rows = cursor.fetchall()
        cursor.close()
        db.close()
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/alerts", methods=["GET"])
def get_alerts():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM alert_logs ORDER BY timestamp DESC LIMIT 20")
        rows = cursor.fetchall()
        cursor.close()
        db.close()
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/thresholds", methods=["GET"])
def get_thresholds():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM alert_thresholds")
        rows = cursor.fetchall()
        cursor.close()
        db.close()
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/thresholds", methods=["POST"])
def set_threshold():
    try:
        data = request.json

        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
            INSERT INTO alert_thresholds
            (parameter, min_value, max_value)
            VALUES (%s, %s, %s)
        """, (
            data["parameter"],
            data["min_value"],
            data["max_value"]
        ))

        db.commit()

        cursor.close()
        db.close()

        return jsonify({"message": "Threshold saved!"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/thresholds/<int:id>", methods=["DELETE"])
def delete_threshold(id):

    try:
        db = get_db()
        cursor = db.cursor()

        cursor.execute(
            "DELETE FROM alert_thresholds WHERE id = %s",
            (id,)
        )

        db.commit()

        return jsonify({
            "message": "Threshold deleted"
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500
@app.route("/")
def index():
    return send_from_directory(".", "index.html")
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)