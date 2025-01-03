# TickerTrek - Real-Time Distributed Stock Trading System

## Overview
This project implements a real-time distributed stock trading system to enable traders to make informed buy/sell decisions on Apple stock. The system uses predictive analytics and visualisations of historical market data to simplify decision making for traders. By integrating multiple APIs, machine learning, and a distributed architecture, this system simulates key functionalities of high-frequency trading systems (HFT), excluding automated trade execution.

## Features
- **Real-time price updates** via multiple stock price APIs
- **Machine learning-based predictions** for price movement
- **Historical and aggregated data visualisations**
- **Scalable and fault-tolerant architecture**
- **User-friendly web interface**

## Technology Stack
- **Apache Kafka with KRaft**: For real-time, asynchronous communication
- **Spring Boot**: Backend framework for REST APIs and WebSocket support
- **React**: Frontend for displaying data and visualisations
- **MongoDB**: NoSQL database for storing historical data and predictions
- **Scikit-learn**: Machine learning library for price movement prediction
- **Docker**: Containerisation for easy deployment

## System Architecture
1. **Data Scraper Nodes**: Poll stock price data from APIs (Finnhub, Twelvedata, Stockdata) and publish to Kafka topics.
2. **Prediction Node**: Consume real-time price data, combine with historical data, and predict price movements using machine learning.
3. **Analytics Node**: Provide REST API endpoints and WebSocket streams for real-time and historical data.
4. **Client Node**: React-based frontend to display data and visualizations.

## Configuration
### API Keys
Create a `config.properties` file in the `src/main/resources` directory of each data scraper module (Finnhub, Stockdata, Twelvedata). For stockdata this would look like:
```
stockdata.api.key=API_KEY
```
Replace `API_KEY` with your actual API key. Do likewise for finnhub.api.key and twelvedata.api.key in their respective directories.

### Analytics Node Configuration
Create an `application.properties` file in the `analytics/src/main/resources` directory:
```
spring.kafka.bootstrap-servers=kafka:9092
spring.data.mongodb.uri=mongodb+srv://{username}:{password}@{nameofcluster}.074jo.mongodb.net/{nameofdatabase}
```
Replace `{username}`, `{password}`, `{nameofcluster}`, and `{nameofdatabase}` with your MongoDB shard credentials or the path to your local MongoDB instance.

### .env Configuration
Create a `.env` file in the root directory (i.e. where the docker-compose.yml, etc. are located):
```
ALPHA_VANTAGE_API_KEY=API_KEY
DATABASE_PASSWORD=DB_PASS
```
Replace `API_KEY` and `DB_PASS` with your actual key and password.

## Deployment
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```
2. Ensure Docker, Docker Compose and Maven are installed.
3. Build the JAR files for the modules:
    ```bash
   mvn clean install
    ```
3. Start the services:
   ```bash
   docker compose build && docker compose up
   ```
4. Access the frontend at `http://localhost:5173/`.

Note: the frontend will not display any data for up to a minute after running the docker compose as the analytics service is slow to start.

## Usage
- Monitor real-time price updates and predictions in the web interface.
- Use the visualisations to make informed trading decisions.

## Scalability and Fault Tolerance
- **Kafka**: Distributed, fault-tolerant, and scalable message broker.
- **MongoDB**: Supports sharding and replication for high availability.
- **Spring Boot Microservices**: Easily replicated to handle increased loads.
- **Docker**: Simplifies deployment and recovery.

## Contributors
- **Conor O’Mahony**: Data scraping modules, Kafka setup, and Docker Compose configuration.
- **Thomas Pollock**: Machine learning model, prediction node, and cloud MongoDB setup.
- **Vincentiu Ciuraru-Cucu**: Analytics module, REST APIs, WebSocket endpoints, and frontend development.

## Future Enhancements
- Implement Kubernetes for advanced container orchestration.
- Automated backtesting and regular retraining of the machine learning model.
- Potentially introduce gRPC for efficient inter-service communication.

