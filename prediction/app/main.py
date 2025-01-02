import json
import time
from urllib.parse import quote_plus
import pandas as pd
import schedule
from joblib import load
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
from pymongo import MongoClient
import datetime
from datetime import timedelta
import requests
import io
import numpy as np

# Alpha Vantage API KEY
av_key = quote_plus("K6QQP60C5DSXN8MU")

# MongoDB Cluster = TheGooberCluster
password = quote_plus("C0OZACjKnWMF4GQz")
uri = f"mongodb+srv://thomaspollock:{password}@thegoobercluster.074jo.mongodb.net/?retryWrites=true&w=majority&appName=TheGooberCluster"
client = MongoClient(uri)
db = client["apple_stock"]
collection = db["stock_data"]

#cursor = collection.find().sort("_id", -1).limit(20)
#test = pd.DataFrame(data=cursor).sort_values(by="timestamp", ascending=True).drop(columns=["_id"])
#print(test)

model_file = "models/Logistic_Regression_Model_final.pkl"
try:
    data = load(model_file)
    model = data['model']
    scaler = data['scaler']
except FileNotFoundError:
    print(f"File {model_file} not found")
except Exception as e:
    print(f"Error: {e}")

def update_database():
    # On startup, checks if data from the last 5 days is available in database. If no, updates database to include last 5 days of stock data.
    current_time = datetime.datetime.now()
    target_time = current_time - timedelta(days=5)
    database_time = collection.find({"timestamp": {"$gte": target_time, "$lt": current_time}}).sort("_id", -1).limit(1)
    time_check = pd.DataFrame(data=database_time).sort_values(by="timestamp", ascending=True).drop(columns=["_id"])
    if time_check["timestamp"].iloc[0].strftime("%Y:%m:%d") == current_time.strftime("%Y:%m:%d"):
        print("Database up to date")
        return None
    else:
        print("Database not up to date. Updating now.....")
        # Code below working is dependent on Alpha Vantage API stock data for January being available. Will work if "2025-{month}" is changed to "2024-12" in url but only updates up to Dec 31st.
        """month = current_time.strftime("%m")
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=AAPL&interval=1min&outputsize=full&month=2025-{month}&apikey={av_key}&datatype=csv'
        response = requests.get(url)
        new_data = response.text
        csv_data = pd.read_csv(io.StringIO(new_data))
        csv_data["timestamp"] = pd.to_datetime(csv_data["timestamp"])
        csv_data_td = csv_data[(csv_data["timestamp"] >= target_time)]
        csv_data_td = csv_data_td.drop(columns=["volume"])
        csv_data_td["ticker"] = "AAPL"
        csv_data_td["APIname"] = "alpha_vantage"
        csv_data_td["close_diff"] = csv_data_td["close"].diff().fillna(0)
        csv_data_td["prediction"] = np.where(csv_data_td["close_diff"] >= 0, 1, 0)
        csv_data_td1 = csv_data_td.sort_values(by="timestamp", ascending=True).reset_index(drop=True)
        collection.delete_many({"timestamp": {"$gte": target_time, "$lt": current_time}})
        update = csv_data_td1.to_dict(orient="records")
        collection.insert_many(update)"""

def kafka_input(data):
    # Takes transformed data from "ingestion-service" and converts to readable format for predictions
    data_json = json.loads(data)
    input_data = pd.DataFrame([data_json])
    return input_data

def load_data(input_data, model, scaler):
    # Loads Kafka input data and returns predictions
    input_dataframe = timestamp_feature_creation(input_data)
    cl_local = collection.find().sort("_id", -1).limit(20)
    db_data = pd.DataFrame(data=cl_local).sort_values(by="timestamp", ascending=True).drop(columns=["_id"])

    if len(db_data) < 10:
        print("Insufficient historical data!")
        return None

    input_dataframe = close_feature_creation(input_dataframe, db_data)

    if input_dataframe['close_previous_diff'].isna().any():
        print("NaN values in close_previous_diff. Setting it to 0")
        input_dataframe = input_dataframe.assign(close_previous_diff=input_dataframe['close_previous_diff'].fillna(0.0))

    if input_dataframe['rolling_average_3'].isna().any():
        print("NaN values in 3 day rolling avg. Imputting the close_previous_diff")
        input_dataframe = input_dataframe.assign(rolling_average_3=input_dataframe['rolling_average_3'].fillna(input_dataframe['close_previous_diff']))

    if input_dataframe['rolling_average_5'].isna().any():
        print("NaN values in 5 day rolling avg. Imputting the 3 day rolling avg")
        input_dataframe = input_dataframe.assign(rolling_average_5=input_dataframe['rolling_average_5'].fillna(input_dataframe['rolling_average_3']))

    if input_dataframe['rolling_average_10'].isna().any():
        print("NaN values in 10 day rolling avg. Imputting the 5 day rolling avg")
        input_dataframe = input_dataframe.assign(rolling_average_10=input_dataframe['rolling_average_10'].fillna(input_dataframe['rolling_average_5']))

    model_order = ["ticker", "timestamp", "open", "high", "low", "close", "month", "day", "hour", "minute", "year_2022", "year_2023", "year_2024", "close_diff", "close_previous_diff", "rolling_average_log", "rolling_average_3", "rolling_average_5", "rolling_average_10", "year", "APIname"]
    input_dataframe = input_dataframe.reindex(columns=model_order)
    input_dataframe_scaled = scaler.transform(input_dataframe.drop(columns=["close_diff", "timestamp", "year", "APIname", "ticker"]))
    predictions = model.predict(input_dataframe_scaled)
    input_dataframe["prediction"] = predictions
    # Inserts new data into database, enabling will add too many duplicates to the database and mess with the rolling averages. Messed up averages = :'(
    database_insert(input_dataframe)
    return input_dataframe

def timestamp_feature_creation(input_dataframe):
    # Separates timestamp into time features for model
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
    # Creates rolling average and price difference features based off "close" value
    # hist_data = pd.read_json(historical_data)
    input_dataframe["close_diff"] = hist_data["close"].diff()[0]
    input_dataframe["close_previous_diff"] = hist_data["close_diff"].shift()[0]
    input_dataframe['rolling_average_log'] = hist_data['close_previous_diff'].ewm(span=5, adjust=False).mean()[0]
    input_dataframe['rolling_average_3'] = hist_data['close_previous_diff'].rolling(window=3).mean()[0]
    input_dataframe['rolling_average_5'] = hist_data['close_previous_diff'].rolling(window=5).mean()[0]
    input_dataframe['rolling_average_10'] = hist_data['close_previous_diff'].rolling(window=10).mean()[0]
    return input_dataframe

def database_insert(input_data):
    # Inserts new stock price into MongoDB database
    last_prediction = collection.find().sort("_id", -1).limit(1)
    last_prediction_list = list(collection.find().sort("_id", -1).limit(3))
    lp_dataframe = pd.DataFrame(data=last_prediction).sort_values(by="timestamp", ascending=True).drop(columns=["_id"])
    lp_dataframe_list = pd.DataFrame(last_prediction_list).sort_values(by="timestamp", ascending=True).drop(columns=["_id"])
    last_timestamp = lp_dataframe['timestamp'].iloc[0]
    input_timestamp = input_data['timestamp'].iloc[0]
    last_close_price = input_data['close'].iloc[0]
    last_3_close_prices = lp_dataframe_list['close'].tolist()
    if last_timestamp == input_timestamp:
        print('Same date already available in database. Prediction discarded')
    elif all(close_price == last_close_price for close_price in last_3_close_prices):
        print('Last three predictions have the same closing price. API duplication detected. Prediction discarded.')
    else:
        input_data = input_data.to_dict(orient="records")
        collection.insert_many(input_data)

def kafka_output(input_dataframe):
    # Converts predictions for Kafka stream transfer and sends to "analytics-service" module
    json_string = input_dataframe.to_json(orient='records')
    output = json.loads(json_string)
    output[0]['timestamp'] = output[0]['timestamp'] // 1000
    return output

def kafka_pipeline():
    try:
        consumer = KafkaConsumer('stockData', bootstrap_servers='kafka:9092', value_deserializer=lambda x: x.decode('utf-8'))
        producer = KafkaProducer(bootstrap_servers='kafka:9092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))
        for message in consumer:
            print(f"Message received: {message.value}")
            if 'timestamp' not in message.value:
                print("Error: 'timestamp' key missing in the message")
                continue
            input_data = kafka_input(message.value)
            prediction_data = load_data(input_data, model, scaler)
            output_data = kafka_output(prediction_data)
            future = producer.send('predictions', value=output_data[0])
            future.add_callback(lambda metadata: print(f"Message sent to {metadata.topic}, partition {metadata.partition}, {output_data[0]}"))
            future.add_errback(lambda error: print(f"Error sending message: {error}"))
            producer.flush()
    except KafkaError as ke:
        print(f"Kafka error: {ke}")
    except Exception as e:
        print(f"Error in pipeline: {e}")

update_database()

schedule.every(5).seconds.do(kafka_pipeline)
print("Starting prediction engine...")
while True:
    schedule.run_pending()
    time.sleep(3)