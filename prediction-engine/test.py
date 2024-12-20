#import kafka
#from kafka import KafkaConsumer, KafkaProducer
import pandas as pd
import numpy
import sklearn
import joblib
from joblib import load
import schedule
import time
import json

model_file = "models/Logistic_Regression_Model_no_index.pkl"
data_location = "data/prediction_engine_test_data_final.json"
historical_data = "data/prediction_engine_test_data_30.json"

def kafka_input(data):
    # Takes transformed data from "ingestion-service" and converts to readable format for predictions
    # consumer = KafkaConsumer('input-data', group-id='trading-data-system', bootstrap_servers=['localhost:2000'], value_deserializer=lambda m: json.loads(m.decode('utf-8')))
    # for message in consumer:
    # return message.value
    input_data = pd.read_json(data)
    return input_data.tail(1)

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

def timestamp_feature_creation(input_dataframe):
    # Separates timestamp into time features for model
    #input_dataframe['timestamp'] = pd.to_datetime(input_dataframe['timestamp'], unit='s')
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

def close_feature_creation(input_dataframe):
    # Creates rolling average and price difference features based off "close" value
    hist_data = pd.read_json(historical_data)
    input_dataframe["close_diff"] = hist_data["close"][22:].diff()
    input_dataframe["close_previous_diff"] = hist_data["close_diff"][23:].shift(1)
    input_dataframe['rolling_average_log'] = hist_data['close_previous_diff'][18:].ewm(span=5, adjust=False).mean()
    input_dataframe['rolling_average_3'] = hist_data['close_previous_diff'][18:].rolling(window=3).mean()
    input_dataframe['rolling_average_5'] = hist_data['close_previous_diff'][18:].rolling(window=5).mean()
    input_dataframe['rolling_average_10'] = hist_data['close_previous_diff'][12:].rolling(window=10).mean()
    return input_dataframe

def load_data(input_data, model, scaler):
    # Loads Kafka input data and returns predictions
    #input_dataframe = pd.read_json(input_data)
    input_dataframe = timestamp_feature_creation(input_data)
    input_dataframe = close_feature_creation(input_dataframe)
    input_dataframe_scaled = scaler.transform(input_dataframe.drop(columns=["close", "close_diff", "timestamp", "year"]))
    predictions = model.predict(input_dataframe_scaled)
    input_dataframe["prediction"] = predictions
    return input_dataframe

def kafka_output(input_dataframe):
    # Converts predictions for Kafka stream transfer and sends to "analytics-service" module
    #producer = KafkaProducer(bootstrap_servers=['localhost:2001'], value_serializer=lambda v: json.dumps(v).encode('utf-8'))
    #if b[0] == 1:
    #    producer.send('input_data', {'key': b, 'message': "Up"})
    #elif b[0] == 0:
    #    producer.send('input_data', {'key': b, 'message': "Down"})
    #producer.flush()
    json_string = input_dataframe.to_json()
    output = json.loads(json_string)
    return output

def test_run():
    a = kafka_input(data_location)
    b = model_load(model_file)
    if b and b[0] and b[1]:
        c = load_data(a, b[0], b[1])
        d = kafka_output(c)
        return print(d)

#a = kafka_input(data_location)
#b = model_load(model_file)
#c = load_data(a, b[0], b[1])
#d = kafka_output(c)
#e = test_run()
#print(e["timestamp"]["492095"])

print("Starting the prediction engine...")
schedule.every(5).seconds.do(test_run)
while True:
    schedule.run_pending()
    time.sleep(1)