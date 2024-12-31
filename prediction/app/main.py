import schedule
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
import pandas as pd
from joblib import load
import json
from pymongo import MongoClient
from urllib.parse import quote_plus
import time

# MongoDB Cluster = TheGooberCluster
password = quote_plus("C0OZACjKnWMF4GQz")
uri = f"mongodb+srv://thomaspollock:{password}@thegoobercluster.074jo.mongodb.net/?retryWrites=true&w=majority&appName=TheGooberCluster"
client = MongoClient(uri)
db = client["apple_stock"]
collection = db["stock_data"]

cursor = collection.find().sort("_id", -1).limit(20)
test = pd.DataFrame(data=cursor).sort_values(by="timestamp", ascending=True).drop(columns=["_id"])
print(test)

model_file = "models/Logistic_Regression_Model_final.pkl"
try:
    data = load(model_file)
    model = data['model']
    scaler = data['scaler']
except FileNotFoundError:
    print(f"File {model_file} not found")
except Exception as e:
    print(f"Error: {e}")

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
    input_dataframe = close_feature_creation(input_dataframe, db_data)
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
    input_dataframe['year_2024'] = 1
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
    lp_dataframe = pd.DataFrame(data=last_prediction).sort_values(by="timestamp", ascending=True).drop(columns=["_id"])
    last_timestamp = lp_dataframe['timestamp'].iloc[0]  # Get the most recent timestamp value
    input_timestamp = input_data['timestamp'].iloc[0]
    if last_timestamp == input_timestamp:
        print('Duplicate prediction discarded')
        pass
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

schedule.every(5).seconds.do(kafka_pipeline)
print("Starting prediction engine...")
while True:
    schedule.run_pending()
    time.sleep(3)