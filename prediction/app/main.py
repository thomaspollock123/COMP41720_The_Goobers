import datetime
import io
import os
import json
import time
from datetime import timedelta

import numpy as np
import pandas as pd
import requests
import schedule
from joblib import load
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
from pymongo import MongoClient

av_key = os.getenv("ALPHA_VANTAGE_API_KEY")
db_password = os.getenv("DATABASE_PASSWORD")

# MongoDB cluster configuration
uri = (f"mongodb+srv://thomaspollock:{db_password}@thegoobercluster.074jo.mongodb.net/?retryWrites=true&w=majority"
       f"&appName=TheGooberCluster")
client = MongoClient(uri)
db = client["apple_stock"]
collection = db["stock_data"]

model_file = "models/Logistic_Regression_Model_final.pkl"
# Loads stock prediction model into prediction service
try:
    data = load(model_file)
    model = data['model']
    scaler = data['scaler']
except FileNotFoundError:
    print(f"File {model_file} not found")
except Exception as e:
    print(f"Error: {e}")


def update_database():
    """On startup, checks if data from the last 5 days is available in database.
    If not, updates database to include last 5 days of stock data."""
    current_time = datetime.datetime.now()
    # target_time = 5 days prior to "current_time"
    target_time = current_time - timedelta(days=5)
    database_time = collection.find({"timestamp": {"$gte": target_time, "$lt": current_time}}).sort("_id", -1).limit(1)
    time_check = pd.DataFrame(data=database_time).sort_values(by="timestamp", ascending=True).drop(columns=["_id"])

    # Compares latest timestamp from database to the current time
    if time_check["timestamp"].iloc[0].strftime("%Y:%m:%d") == current_time.strftime("%Y:%m:%d"):
        print("Database up to date")
        return None
    else:
        print("Database not up to date. Updating now.....")
        month = current_time.strftime("%m")
        url = (f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=AAPL&interval=1min&outputsize'
               f'=full&month=2025-{month}&apikey={av_key}&datatype=csv')
        try:
            # Requests this month's historical stock data from Alpha Vantage API
            response = requests.get(url)
            response.raise_for_status()
            new_data = response.text
            csv_data = pd.read_csv(io.StringIO(new_data))
        except requests.exceptions.RequestException as e:
            # Returns None and prediction service continues initialization if data isn't available or connection
            # error occurs
            print(f"Failed to update database: {e}. \nProceeding with stock predictions...")
            return None

        # Incoming API data transformed to adhere to system data requirements
        csv_data["timestamp"] = pd.to_datetime(csv_data["timestamp"])
        # Filters last 5 days of data from API call
        csv_data_td = csv_data[(csv_data["timestamp"] >= target_time)]
        csv_data_td = csv_data_td.drop(columns=["volume"])
        csv_data_td["ticker"] = "AAPL"
        csv_data_td["APIname"] = "alpha_vantage"

        # Predictions added automatically to incoming historical data to avoid delay on start-up
        csv_data_td["close_diff"] = csv_data_td["close"].diff().fillna(0)
        csv_data_td["close_previous_diff"] = csv_data_td["close_diff"].shift().fillna(0)
        csv_data_td["prediction"] = np.where(csv_data_td["close_diff"] >= 0, 1, 0)
        csv_data_td1 = csv_data_td.sort_values(by="timestamp", ascending=True).reset_index(drop=True)
        collection.delete_many({"timestamp": {"$gte": target_time, "$lt": current_time}})

        update = csv_data_td1.to_dict(orient="records")
        collection.insert_many(update)
        print("Successfully updated the database!")


def kafka_input(data):
    """Takes data from KafkaConsumer data stream and
    converts to readable Pandas dataframe for transformations and predictions"""
    data_json = json.loads(data)
    input_data = pd.DataFrame([data_json])
    return input_data


def load_data(input_data, model, scaler):
    """Loads Kafka input data and returns predictions"""
    input_dataframe = timestamp_feature_creation(input_data)
    # "last_20" = latest 20 stock prediction records added to database
    last_20 = collection.find().sort("_id", -1).limit(20)
    # "db_data" = Dataframe derived from "last_20"
    db_data = pd.DataFrame(data=last_20).sort_values(by="timestamp", ascending=True).drop(columns=["_id"])

    if len(db_data) < 10:
        print("Insufficient historical data!")
        return None

    input_dataframe = close_feature_creation(input_dataframe, db_data)

    input_dataframe.fillna({
        'close_previous_diff': 0.0,
        'rolling_average_3': input_dataframe['close_previous_diff'],
        'rolling_average_5': input_dataframe['rolling_average_3'],
        'rolling_average_10': input_dataframe['rolling_average_5']
    }, inplace=True)

    model_order = ["ticker", "timestamp", "open", "high", "low", "close", "month", "day", "hour", "minute", "year_2022", "year_2023", "year_2024", "close_diff", "close_previous_diff", "rolling_average_log", "rolling_average_3", "rolling_average_5", "rolling_average_10", "year", "APIname"]
    input_dataframe = input_dataframe.reindex(columns=model_order)
    # StandardScaler applied to model features
    input_dataframe_scaled = scaler.transform(
        input_dataframe.drop(columns=["close_diff", "timestamp", "year", "APIname", "ticker"]))
    # Prediction features = open, high, low, close, month, day, hour, minute, year_2022, year_2023, year_2024,
    # close_previous_diff, rolling_average_log, rolling_average_3, rolling_average_5, rolling_average_10
    predictions = model.predict(input_dataframe_scaled)
    # "predictions" = 0 (stock price goes down), 1 (stock price goes up)
    input_dataframe["prediction"] = predictions
    database_insert(input_dataframe)
    return input_dataframe


def timestamp_feature_creation(input_dataframe):
    """Separates timestamp into time features for prediction model"""
    if 'timestamp' not in input_dataframe.columns:
        raise KeyError("'timestamp' column missing in input dataframe")

    input_dataframe['timestamp'] = pd.to_datetime(input_dataframe['timestamp'], unit='s')
    input_dataframe['timestamp'] = input_dataframe['timestamp'].astype('datetime64[ns]')
    input_dataframe['year'] = input_dataframe['timestamp'].dt.year
    input_dataframe['month'] = input_dataframe['timestamp'].dt.month
    input_dataframe['day'] = input_dataframe['timestamp'].dt.day
    input_dataframe['hour'] = input_dataframe['timestamp'].dt.hour
    input_dataframe['minute'] = input_dataframe['timestamp'].dt.minute
    input_dataframe['year_2022'] = 0
    input_dataframe['year_2023'] = 0
    input_dataframe['year_2024'] = 0
    input_dataframe['year_2025'] = 1
    return input_dataframe


def close_feature_creation(input_dataframe, hist_data):
    """Creates rolling average and price difference features
    based off of "close" value from incoming stock price

    "close_diff" = difference between current stock price and latest added to database
    "close_previous_diff" = previous "close_diff" price from last price added
    'rolling_average_log' = exponentially weighted moving average of the last 5 prices
    'rolling_average_3' = rolling average of the last 3 prices
    'rolling_average_5' = rolling average of the last 5 prices
    'rolling_average_10' = rolling average of the last 10 prices
    """

    # Ensure there is sufficient historical data and the 'close' column exists
    if hist_data.empty or 'close' not in hist_data.columns:
        print("Historical data is empty or missing 'close'. Defaulting all features to 0")
        input_dataframe["close_diff"] = input_dataframe["close_previous_diff"] = input_dataframe['rolling_average_log'] = input_dataframe['rolling_average_3'] = input_dataframe['rolling_average_5'] = input_dataframe['rolling_average_10'] = 0
        return input_dataframe

    # Calculate close_diff and create close_previous_diff
    hist_data["close_diff"] = hist_data["close"].diff()
    hist_data["close_previous_diff"] = hist_data["close_diff"].shift()

    # Propagate close_previous_diff to the input dataframe
    input_dataframe["close_previous_diff"] = hist_data["close_previous_diff"].iloc[0] if not hist_data["close_previous_diff"].isnull().all() else None

    # If 'close_previous_diff' is entirely NaN, return NaN for rolling averages
    if hist_data["close_previous_diff"].isnull().all():
        print("'close_previous_diff' contains only NaN values. Rolling averages will default to 0.")
        input_dataframe["close_diff"] = input_dataframe["close_previous_diff"] = input_dataframe['rolling_average_log'] = input_dataframe['rolling_average_3'] = input_dataframe['rolling_average_5'] = input_dataframe['rolling_average_10'] = 0
        return input_dataframe

    # Calculate rolling averages
    valid_data = hist_data["close_previous_diff"].dropna()

    if len(valid_data) < 10:
        print("Insufficient rows in 'close_previous_diff' for rolling averages. Defaulting to 0.")
        input_dataframe['rolling_average_log'] = input_dataframe['rolling_average_3'] = input_dataframe['rolling_average_5'] = input_dataframe['rolling_average_10'] = 0
    else:
        rolling_avg_log = valid_data.ewm(span=5, adjust=False).mean().iloc[-1]
        rolling_avg_3 = valid_data.rolling(window=3).mean().iloc[-1]
        rolling_avg_5 = valid_data.rolling(window=5).mean().iloc[-1]
        rolling_avg_10 = valid_data.rolling(window=10).mean().iloc[-1]

        input_dataframe['rolling_average_log'] = rolling_avg_log
        input_dataframe['rolling_average_3'] = rolling_avg_3
        input_dataframe['rolling_average_5'] = rolling_avg_5
        input_dataframe['rolling_average_10'] = rolling_avg_10

    return input_dataframe


def database_insert(input_data):
    """Inserts new stock price into MongoDB database"""
    # last_prediction = last prediction added to database
    last_prediction = collection.find().sort("_id", -1).limit(1)
    # last_prediction_list = last 3 predictions added to database
    last_prediction_list = list(collection.find().sort("_id", -1).limit(3))

    lp_dataframe = pd.DataFrame(data=last_prediction).sort_values(by="timestamp", ascending=True).drop(columns=["_id"])
    lp_dataframe_list = pd.DataFrame(last_prediction_list).sort_values(by="timestamp", ascending=True).drop(
        columns=["_id"])

    last_timestamp = lp_dataframe['timestamp'].iloc[0]
    input_timestamp = input_data['timestamp'].iloc[0]
    last_close_price = input_data['close'].iloc[0]
    last_3_close_prices = lp_dataframe_list['close'].tolist()

    # Compares timestamp of current prediction of last prediction added
    if last_timestamp == input_timestamp:
        print('Same date already available in database. Prediction discarded')
    # Compares current timestamp to last 3 predictions added
    elif all(close_price == last_close_price for close_price in last_3_close_prices):
        print('Last three predictions have the same closing price. API duplication detected. Prediction discarded.')
    else:
        input_data = input_data.to_dict(orient="records")
        collection.insert_many(input_data)


def kafka_output(input_dataframe):
    """Configures prediction data for Kafka stream transfer"""
    json_string = input_dataframe.to_json(orient='records')
    output = json.loads(json_string)
    # Bug fix for additional zeroes added to "timestamp" epoch value after
    # dataframe-json conversion
    output[0]['timestamp'] = output[0]['timestamp'] // 1000
    return output


def kafka_pipeline():
    """
    Function for configuring and executing Kafka pipeline for prediction engine/'prediction' service.

    Consumes incoming stock data from the 'stockData' topic stream, orchestrates key data transformation and
    prediction functions and sends the data through the 'predictions' topic stream for use in the
    'analytics' service.
     """
    print("Starting Kafka pipeline...")
    try:
        # consumer = KafkaConsumer, fetches currently available data from "stockData" topic stream and
        # deserializes input using lambda function
        consumer = KafkaConsumer('stockData', bootstrap_servers='kafka:9092',
                                 value_deserializer=lambda x: x.decode('utf-8'))
        # producer = KafkaProducer, takes transformed prediction data from prediction engine, serializes it and
        # sends it to "prediction" topic stream for use in "analytics" service front-end
        producer = KafkaProducer(bootstrap_servers='kafka:9092',
                                 value_serializer=lambda v: json.dumps(v).encode('utf-8'))
        for message in consumer:
            print(f"Message received: {message.value}")
            if 'timestamp' not in message.value:
                print("Error: 'timestamp' key missing in the message")
                continue

            # Deserialized KafkaConsumer output passed through "kafka_input()" function
            input_data = kafka_input(message.value)
            prediction_data = load_data(input_data, model, scaler)
            if prediction_data is not None:
                output_data = kafka_output(prediction_data)
                # Array-enclosed "output_data" sent through producer topic stream to "analytics" service
                future = producer.send('predictions', value=output_data[0])
                future.add_callback(lambda metadata: print(
                    f"Message sent to {metadata.topic}, partition {metadata.partition}, {output_data[0]}"))
                future.add_errback(lambda error: print(f"Error sending message: {error}"))
                producer.flush()
    except KafkaError as ke:
        print(f"Kafka error: {ke}")
    except Exception as e:
        print(f"Error in pipeline: {e}")


print("Starting prediction engine...")
# "update_database()" run to ensure the database is up-to-date in case of prolong inactivity.
update_database()
schedule.every(5).seconds.do(kafka_pipeline)
while True:
    schedule.run_pending()
    time.sleep(3)
