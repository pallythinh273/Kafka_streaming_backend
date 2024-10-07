from confluent_kafka import Consumer, KafkaException, KafkaError
import psycopg2
import os
import json

KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
WEATHER_TOPIC = os.environ.get("WEATHER_TOPIC", "weather")
AIR_POLLUTION_TOPIC = os.environ.get("AIR_POLLUTION_TOPIC", "air_pollution")

## Config for PostgreSQL
db_config = {
    "dbname": "weather_db",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": "5433",
}

# Connect to PostgreSQL Database
try:
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
    print("Connected to PostgreSQL database.")
except Exception as e:
    print(f"Failed to connect to PostgreSQL: {e}")
    exit(1)

# Create weather and air_pollution tables
create_weather_table_query = """
CREATE TABLE IF NOT EXISTS weather (
    id UUID PRIMARY KEY,
    timestamp TIMESTAMP,
    temperature FLOAT,
    humidity FLOAT,
    pressure FLOAT,
    wind_speed FLOAT,
    wind_direction FLOAT,
    sea_level FLOAT,
    description TEXT,
    icon TEXT
);
"""
create_air_pollution_table_query = """
CREATE TABLE IF NOT EXISTS air_pollution (
    id UUID PRIMARY KEY,
    timestamp TIMESTAMP,
    aqi INTEGER,
    pm2_5 FLOAT,
    pm10 FLOAT,
    o3 FLOAT,
    no2 FLOAT,
    so2 FLOAT,
    co FLOAT
);
"""
cursor.execute(create_weather_table_query)
cursor.execute(create_air_pollution_table_query)
conn.commit()


def insert_weather_data_to_postgres(data, table_name):
    insert_query = f"""
    INSERT INTO {table_name} (id, timestamp, temperature, humidity, pressure, wind_speed, wind_direction, sea_level, description, icon)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """
    cursor.execute(
        insert_query,
        (
            data["id"],
            data["timestamp"],
            data["temperature"],
            data["humidity"],
            data["pressure"],
            data["wind_speed"],
            data["wind_direction"],
            data["sea_level"],
            data["description"],
            data["icon"],
        ),
    )
    conn.commit()
    print(f"Inserted data to {table_name} table.")


def insert_air_pollution_data_to_postgres(data, table_name):
    insert_query = f"""
    INSERT INTO {table_name} (id, timestamp, aqi, pm2_5, pm10, o3, no2, so2, co)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
    """
    cursor.execute(
        insert_query,
        (
            data["id"],
            data["timestamp"],
            data["aqi"],
            data["pm2_5"],
            data["pm10"],
            data["o3"],
            data["no2"],
            data["so2"],
            data["co"],
        ),
    )
    conn.commit()
    print(f"Inserted data to {table_name} table.")


def consume_data_from_kafka():
    consumer = Consumer(
        {
            "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
            "group.id": "weather_consumer",
            "auto.offset.reset": "earliest",
        }
    )

    consumer.subscribe([WEATHER_TOPIC, AIR_POLLUTION_TOPIC])

    try:
        while True:
            message = consumer.poll(timeout=1.0)
            if message is None:
                continue
            if message.error():
                if message.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    raise KafkaException(message.error())
            else:
                # Decode the message and load as JSON
                data = json.loads(message.value().decode("utf-8"))
                topic = message.topic()

                # Insert into the appropriate table
                if topic == WEATHER_TOPIC:
                    insert_weather_data_to_postgres(data, "weather")
                elif topic == AIR_POLLUTION_TOPIC:
                    insert_air_pollution_data_to_postgres(data, "air_pollution")

    except KeyboardInterrupt:
        print("Consumer interrupted by user")
    finally:
        consumer.close()
        cursor.close()
        conn.close()


if __name__ == "__main__":
    consume_data_from_kafka()
