#import kafka
#from kafka import KafkaConsumer, KafkaProducer
import pandas as pd
import numpy
import sklearn
import joblib
from joblib import load
import json

model_file = "models/Logistic_Regression_Model_no_index.pkl"
data_location = "data/prediction_engine_test_data_30.json"

def kafka_input():
    # Takes transformed data from "ingestion-service" and converts to readable format for predictions
    # consumer = KafkaConsumer('input-data', group-id='trading-data-system', bootstrap_servers=['localhost:2000'], value_deserializer=lambda m: json.loads(m.decode('utf-8')))
    # for message in consumer:
    # return message.value
    pass

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
    input_dataframe = pd.read_json(input_data)
    input_dataframe = pd.read_json(input_data).drop(columns=["timestamp", "close", "close_diff", "close_sp500", "close_nasdaq_100", "close_nasdaq_com", "close_cboe"])
    input_dataframe = scaler.transform(input_dataframe)
    predictions = model.predict(input_dataframe)
    return predictions

#if a:
#    print(a)
a = model_load(model_file)
b = load_data(data_location, a[0], a[1])
print(b)

def kafka_output():
    # Converts predictions for Kafka stream transfer and sends to "analytics-service" module
    #producer = KafkaProducer(bootstrap_servers=['localhost:2001'], value_serializer=lambda v: json.dumps(v).encode('utf-8'))
    #if b[0] == 1:
    #    producer.send('input_data', {'key': b, 'message': "Up"})
    #elif b[0] == 0:
    #    producer.send('input_data', {'key': b, 'message': "Down"})
    #producer.flush()
    pass