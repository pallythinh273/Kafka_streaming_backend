# Kafka Streaming Backend

Implement Kafka and PostgreSQL on Docker

Get the API key from OpenWeatherMap in put on jobs/config.py and longitude, latitude you want to collect

### Create folder local for PostgreSQL Data
```bash
mkdir psql_data
```
### Run the Docker compose file to start the services

```bash
docker compose up -d
```

### Install library
```bash
pip install -r requirements.txt
```

### Next step, run Producer and Consumer with Kafka to collect the data on OpenWeatherMap
```bash
python job/producer.py
```
### Run another Terminal:
```bash
python job/consumer.py
```

# Check the data on PostgreSQL

```bash
docker exec -it postgres psql -U postgres -d weather_db
```
```bash
SELECT * FROM weather;
```
```bash
SELECT * FROM air_polution;
```
