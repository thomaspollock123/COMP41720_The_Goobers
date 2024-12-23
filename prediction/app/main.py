import schedule
from kafka import KafkaProducer, KafkaConsumer, KafkaAdminClient
from datetime import datetime
import pandas as pd
from joblib import load
import json
from pymongo import MongoClient
from urllib.parse import quote_plus
import time

"""try:
    print('Welcome to parse engine')
    consumer = KafkaConsumer('stockData', bootstrap_servers='kafka:9092', value_deserializer=lambda x: json.loads(x.decode('utf-8')))
    for message in consumer:
        print(message)
except Exception as e:
    print(e)"""

# MongoDB Cluster = TheGooberCluster
password = quote_plus("C0OZACjKnWMF4GQz")
uri = f"mongodb+srv://thomaspollock:{password}@thegoobercluster.074jo.mongodb.net/?retryWrites=true&w=majority&appName=TheGooberCluster"
client = MongoClient(uri)
db = client["apple_stock"]
collection = db["stock_data"]
cl = collection.find().sort("_id", -1).limit(20)
db_data = pd.DataFrame(data=cl).sort_values(by="timestamp", ascending=True).drop(columns=["_id"])

"""client_local = MongoClient()
db_local = client_local["apple_stock"]
collection_local = db_local["stock_data"]
cl_local = collection_local.find().sort("_id", -1).limit(20)
db_data_local = pd.DataFrame(data=cl_local).sort_values(by="timestamp", ascending=True).drop(columns=["_id"])
print(db_data_local)
cl_local = collection_local.find().sort("_id", -1).limit(1)
db_data_local = pd.DataFrame(data=cl_local).sort_values(by="timestamp", ascending=True).drop(columns=["_id"])
insert_data = db_data_local.to_dict(orient="records")
collection_local.insert_one({"APIname": "finnhub", "timestamp": datetime(2024, 12, 12, 21, 59, 29), "open": 248.04, "close": 254.49, "high": 255.0, "low": 245.69})
last_insert = collection_local.find_one(sort=[("_id", -1)])
collection_local.delete_one({"_id": last_insert["_id"]})
cl_local = collection_local.find().sort("_id", -1).limit(6)
db_data_test = pd.DataFrame(data=cl_local).sort_values(by="timestamp", ascending=True).drop(columns=["_id"])
print(db_data_test)"""

# cl = collection.find().sort("_id", -1).limit(20)
# db_data = pd.DataFrame(data=cl).sort_values(by="timestamp", ascending=True).drop(columns=["_id"])
model_file = "models/Logistic_Regression_Model_final.pkl"

def kafka_input(data):
    # Takes transformed data from "ingestion-service" and converts to readable format for predictions
    input_data = pd.DataFrame([data])
    return input_data

def model_load(model_data):
    # Loads model into process
    try:
        data = load(model_data)
        model = data['model']
        scaler = data['scaler']
        return model, scaler
    except FileNotFoundError:
        print(f"File {model_data} not found")
    except Exception as e:
        print(f"Error: {e}")

def load_data(input_data, model, scaler):
    # Loads Kafka input data and returns predictions
    input_dataframe = timestamp_feature_creation(input_data)
    input_dataframe = close_feature_creation(input_dataframe, db_data)
    model_order = ["timestamp", "open", "high", "low", "close", "month", "day", "hour", "minute", "year_2022", "year_2023", "year_2024", "close_diff", "close_previous_diff", "rolling_average_log", "rolling_average_3", "rolling_average_5", "rolling_average_10", "year", "APIname"]
    input_dataframe = input_dataframe.reindex(columns=model_order)
    input_dataframe_scaled = scaler.transform(input_dataframe.drop(columns=["close_diff", "timestamp", "year", "APIname"]))
    predictions = model.predict(input_dataframe_scaled)
    input_dataframe["prediction"] = predictions
    # Inserts new data into database, enabling will add too many duplicates to the database and mess with the rolling averages. Messed up averages = :'(
    #database_insert(input_dataframe)
    return input_dataframe

def timestamp_feature_creation(input_dataframe):
    # Separates timestamp into time features for model
    # input_dataframe['timestamp'] = pd.to_datetime(input_dataframe['timestamp'], unit='s')
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
    input_data = input_data.to_dict(orient="records")
    collection.insert_many(input_data)

def kafka_output(input_dataframe):
    # Converts predictions for Kafka stream transfer and sends to "analytics-service" module
    json_string = input_dataframe.to_json(orient='records')
    output = json.loads(json_string)
    return output

def test_run():
    a = kafka_input({"APIname": "finnhub", "timestamp": datetime(2024, 12, 12, 21, 59, 29), "open": 248.04, "close": 254.49, "high": 255.0, "low": 245.69})
    b = model_load(model_file)
    if b and b[0] and b[1]:
        c = load_data(a, b[0], b[1])
        d = kafka_output(c)
        return d

def kafka_output2():
    try:
        #print('Goodbye to parse engine')
        prediction_data = test_run()
        producer = KafkaProducer(bootstrap_servers='kafka:9092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))
        producer.send('stockData', prediction_data[0])
        producer.flush()
    except Exception as e:
        print(e)

kafka_output2()

"""try:
    print('Goodbye to parse engine')
    producer = KafkaProducer(bootstrap_servers='kafka:9092')
    producer.send('finnhub', value=test_run())
    producer.flush()
except Exception as e:
    print(e)
    pass"""

print("Starting the prediction engine...")
schedule.every(5).seconds.do(kafka_output2)
while True:
    schedule.run_pending()
    time.sleep(1)