# Ingestify

**Ingestify** is a data ingestion, refinement, and visualization pipeline designed to process and manage real-time data streams, store data in scalable storage systems, and make the refined data accessible for analysis and visualization. The pipeline integrates Kafka, MinIO, ClickHouse, and Metabase to provide a complete solution for real-time data processing.

## Project Overview

Ingestify is built to handle large volumes of data by consuming events from Kafka topics, storing them in MinIO for temporary storage, processing and refining data in ClickHouse, and providing an API to serve refined data for visualization via Metabase.

### Core Components
1. **Kafka**: Serves as the event streaming platform where data is ingested in real-time from various producers.
2. **MinIO**: Used for storing raw event data temporarily before processing.
3. **ClickHouse**: A columnar database for storing refined and aggregated data, optimized for analytical queries.
4. **Metabase**: A business intelligence tool for visualizing the refined data stored in ClickHouse via an API.
5. **API**: A RESTful API to serve the refined data from ClickHouse to Metabase.

## Project Architecture

The architecture of **Ingestify** can be divided into the following main components:
- **Producer**: Generates and produces events to Kafka topics (e.g., `user-events`, `order-events`).
- **Consumer**: Consumes events from Kafka topics, stores raw data into MinIO, and processes it to refine and store in ClickHouse.
- **ClickHouse**: Stores refined data for querying and analysis.
- **Metabase**: Fetches data from ClickHouse via the API to visualize insights in dashboards.
  
## Setup and Installation

### Prerequisites

1. **Docker** - To run Kafka, MinIO, ClickHouse, and Metabase.
2. **Python 3.9+** - Required for running the data processing and API components.
3. **Kafka** - Event streaming service.
4. **ClickHouse** - Analytical database for storing refined data.
5. **MinIO** - Object storage for raw event data.
6. **Metabase** - BI tool for visualizing data.

### Environment Variables

The following environment variables must be set in your `.env` file for the project:

```env
KAFKA_SERVER=localhost:9092
KAFKA_TOPICS=user-events,order-events
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=MB30ZIE4qBwPSS775NBB
MINIO_SECRET_KEY=FqHf5e2fuWilZPPVeYQWkgIdhjmANQ9tAyDEjTL6
BUCKET_NAME=data-lake
```

### Docker Compose Setup

Ingestify uses Docker Compose to spin up the necessary services for Kafka, MinIO, ClickHouse, and Metabase. Below is the `docker-compose.yml` for setting up the environment:

```yaml
version: '3'
services:
  zookeeper:
    image: wurstmeister/zookeeper:3.4.6
    ports:
      - "2181:2181"
  kafka:
    image: wurstmeister/kafka:latest
    ports:
      - "9092:9092"
    environment:
      KAFKA_ADVERTISED_LISTENERS: INSIDE://kafka:9093, OUTSIDE://localhost:9092
      KAFKA_LISTENER_SECURITY_PROTOCOL: PLAINTEXT
      KAFKA_LISTENER_NAMES: INSIDE, OUTSIDE
      KAFKA_LISTENER_PORT: 9093
      KAFKA_LISTENER_INSIDE_PORT: 9092
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
    depends_on:
      - zookeeper

  minio:
    image: minio/minio:latest
    ports:
      - "9000:9000"
    environment:
      MINIO_ACCESS_KEY: "MB30ZIE4qBwPSS775NBB"
      MINIO_SECRET_KEY: "FqHf5e2fuWilZPPVeYQWkgIdhjmANQ9tAyDEjTL6"
    command: server /data

  clickhouse:
    image: yandex/clickhouse-server:latest
    ports:
      - "8123:8123"
      - "9000:9000"
    environment:
      CLICKHOUSE_DB: default

  metabase:
    image: metabase/metabase:latest
    ports:
      - "3000:3000"
    environment:
      MB_DB_TYPE: "postgres"
      MB_DB_DBNAME: "metabase"
      MB_DB_PORT: "5432"
      MB_DB_USER: "metabase"
      MB_DB_PASS: "metabase"
    depends_on:
      - clickhouse
```

### Running the Project

1. **Start the services** with Docker Compose:
   ```bash
   docker-compose up -d
   ```

2. **Start the Kafka producer and consumer**:
   - Run the producer script to generate and send events to Kafka:
     ```bash
     python producer.py
     ```
   - Run the consumer script to consume messages, store raw data in MinIO, and refine data into ClickHouse:
     ```bash
     python consumer.py
     ```

3. **Start the API server** to serve data to Metabase:
   ```bash
   python api.py
   ```

4. **Connect Metabase to ClickHouse**:
   - Access Metabase at `http://localhost:3000`.
   - Set up a new data source for ClickHouse with the connection details provided by Docker Compose (`localhost:8123`).

## Features

- **Real-Time Event Streaming**: Consume events from Kafka topics and process them in real-time.
- **Data Storage**: Raw events are stored in MinIO, while refined data is stored in ClickHouse for fast analytical querying.
- **Data Visualization**: Metabase allows you to create dashboards and visualizations based on the refined data in ClickHouse.
- **API for Serving Data**: Expose an API to serve the refined data to Metabase or other consumers.

## Contribution

Feel free to fork this repository and create pull requests. Contributions are welcome!
