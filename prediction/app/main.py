import schedule
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
from datetime import datetime
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

model_file = "models/Logistic_Regression_Model_final.pkl"
try:
    data = load(model_file)
    model = data['model']
    scaler = data['scaler']
except FileNotFoundError:
    print(f"File {model_file} not found")
except Exception as e:
    print(f"Error: {e}")

def input_preprocessing(data):
    # Converts "ingestion-service" KafkaProducer data stream input to JSON format
    try:
        if data.startswith("Stock{") and data.endswith("}"):
            data = data[len("Stock{"):-1]
        data = data.replace("=", ":").replace("'", '"')
        data = data.replace("APIname", "\"APIname\"")
        data = data.replace("timestamp", "\"timestamp\"")
        data = data.replace("open", "\"open\"")
        data = data.replace("close", "\"close\"")
        data = data.replace("high", "\"high\"")
        data = data.replace("low", "\"low\"")
        return "{" + data + "}"
    except Exception as e:
        raise ValueError(f"Failed to preprocess data to JSON: {data}. Error: {e}")

def kafka_input(data):
    # Takes transformed data from "ingestion-service" and converts to readable format for predictions
    data_input = input_preprocessing(data)
    print(data_input)
    data_json = json.loads(data_input)
    print(data_json)
    input_data = pd.DataFrame([data_json])
    return input_data

"""def model_load(model_data):
    # Loads model into process
    try:
        data = load(model_data)
        model = data['model']
        scaler = data['scaler']
        return model, scaler
    except FileNotFoundError:
        print(f"File {model_data} not found")
    except Exception as e:
        print(f"Error: {e}")"""

def load_data(input_data, model, scaler):
    # Loads Kafka input data and returns predictions
    input_dataframe = timestamp_feature_creation(input_data)
    cl_local = collection.find().sort("_id", -1).limit(20)
    db_data = pd.DataFrame(data=cl_local).sort_values(by="timestamp", ascending=True).drop(columns=["_id"])
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
    input_data = input_data.to_dict(orient="records")
    collection.insert_many(input_data)

def kafka_output(input_dataframe):
    # Converts predictions for Kafka stream transfer and sends to "analytics-service" module
    json_string = input_dataframe.to_json(orient='records')
    print(json_string)
    output = json.loads(json_string)
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
            future = producer.send('stockData', value=output_data[0])
            future.add_callback(lambda metadata: print(f"Message sent to {metadata.topic}, partition {metadata.partition}"))
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
    time.sleep(1)

"""def test_run():
    consumer = KafkaConsumer('stockData', bootstrap_servers='kafka:9092', value_deserializer=lambda x: json.loads(x.decode('utf-8')))
    for message in consumer:
        print(f"Received message: {message.value}")
    ab = message.value
    #a = kafka_input({"APIname": "finnhub", "timestamp": datetime(2024, 12, 12, 21, 59, 29), "open": 248.04, "close": 254.49, "high": 255.0, "low": 245.69})
    b = model_load(model_file)
    if b and b[0] and b[1]:
        c = load_data(ab, b[0], b[1])
        d = kafka_output(c)
        return d

def kafka_output2():
    try:
        #print('Goodbye to parse engine')
        prediction_data = test_run()
        producer = KafkaProducer(bootstrap_servers='kafka:9092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))
        # Test if Kafka is accessible by sending a message
        def on_send_success(record_metadata):
            print(f"Message sent successfully to {record_metadata.topic} partition {record_metadata.partition} with offset {record_metadata.offset}")
            return
        def on_send_error(excp):
            print(f"Error occurred while sending message: {excp}")
            return
        future = producer.send('stockData', value=prediction_data[0])
        future.add_callback(on_send_success)
        future.add_errback(on_send_error)
        producer.flush()
        print(prediction_data[0])
    except KafkaError as ke:
        print(f"KafkaError: {ke}")
    except Exception as e:
        print(f"An error occurred: {e}")

print("Starting the prediction engine...")
schedule.every(2).seconds.do(kafka_output2)
while True:
    schedule.run_pending()
    time.sleep(2)"""

"""try:
    print('Welcome to parse engine')
    consumer = KafkaConsumer('stockData', bootstrap_servers='kafka:9092', value_deserializer=lambda x: json.loads(x.decode('utf-8')))
    for message in consumer:
        print(message)
except Exception as e:
    print(e)"""

"""cl = collection.find().sort("_id", -1).limit(20)
db_data = pd.DataFrame(data=cl).sort_values(by="timestamp", ascending=True).drop(columns=["_id"])"""

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


"""try:
    print('Goodbye to parse engine')
    producer = KafkaProducer(bootstrap_servers='kafka:9092')
    producer.send('finnhub', value=test_run())
    producer.flush()
except Exception as e:
    print(e)
    pass"""