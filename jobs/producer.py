import os
from confluent_kafka import SerializingProducer
from config import API_KEY, LON, LAT
import simplejson as json
import datetime
import time
import uuid
import requests


KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
# KAFKA_BOOTSTRAP_SERVERS = os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'broker:29092')
VEHICLE_TOPIC = os.environ.get("VEHICLE_TOPIC", "vehicle")
WEATHER_TOPIC = os.environ.get("WEATHER_TOPIC", "weather")
AIR_POLLUTION_TOPIC = os.environ.get("AIR_POLLUTION_TOPIC", "air_pollution")


def get_weather_data():
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={LAT}&lon={LON}&appid={API_KEY}"
    response = requests.get(url).json()

    weather_data = {
        "id": uuid.uuid4(),
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "temperature": response["main"]["temp"],
        "humidity": response["main"]["humidity"],
        "pressure": response["main"]["pressure"],
        "wind_speed": response["wind"]["speed"],
        "wind_direction": response["wind"]["deg"],
        "sea_level": response["main"]["sea_level"],
        "description": response["weather"][0]["description"],
        "icon": response["weather"][0]["icon"],
    }

    return weather_data


def get_air_pollution_data():
    url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={LAT}&lon={LON}&appid={API_KEY}"
    response = requests.get(url).json()

    air_pollution_data = {
        "id": uuid.uuid4(),
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "aqi": response["list"][0]["main"]["aqi"],
        "pm2_5": response["list"][0]["components"]["pm2_5"],
        "pm10": response["list"][0]["components"]["pm10"],
        "o3": response["list"][0]["components"]["o3"],
        "no2": response["list"][0]["components"]["no2"],
        "so2": response["list"][0]["components"]["so2"],
        "co": response["list"][0]["components"]["co"],
    }
    return air_pollution_data


def simulate_journey(producer):
    while True:
        weather_data = get_weather_data()
        air_pollution_data = get_air_pollution_data()
        produce_data_to_kafka(producer, WEATHER_TOPIC, weather_data)
        produce_data_to_kafka(producer, AIR_POLLUTION_TOPIC, air_pollution_data)
        time.sleep(4)


def json_serializer(obj):
    if isinstance(obj, uuid.UUID):
        return str(obj)
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")


def produce_data_to_kafka(producer, topic, data):
    producer.produce(
        topic=topic,
        key=str(data["id"]),
        value=json.dumps(data, default=json_serializer).encode("utf-8"),
        on_delivery=delivery_report,
    )

    producer.flush()


if __name__ == "__main__":
    producer_config = {
        "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
        "error_cb": lambda err: print(f"Kafka Error: {err}"),
    }

    producer = SerializingProducer(conf=producer_config)

    try:
        simulate_journey(producer)

    except KeyboardInterrupt:
        print("Simulation ended by the user")
    except Exception as e:
        print(f"Unexpected Error occured: {e}")
