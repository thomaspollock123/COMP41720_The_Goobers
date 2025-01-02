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
print("Initial historical data (test):")
print(test)

model_file = "models/Logistic_Regression_Model_final.pkl"
try:
    print(f"Loading model from {model_file}...")
    data = load(model_file)
    model = data['model']
    scaler = data['scaler']
    print("Model and scaler loaded successfully.")
except FileNotFoundError:
    print(f"File {model_file} not found")
except Exception as e:
    print(f"Error loading model: {e}")

def kafka_input(data):
    #print("Processing Kafka input data...")
    data_json = json.loads(data)
    #print("Kafka input data converted to JSON:", data_json)
    input_data = pd.DataFrame([data_json])
    #print("Input data DataFrame:")
    #print(input_data)
    return input_data

def load_data(input_data, model, scaler):
    #print("Loading data for predictions...")
    input_dataframe = timestamp_feature_creation(input_data)
    #print("Timestamp features added:")
    #print(input_dataframe)

    cl_local = collection.find().sort("_id", -1).limit(20)
    db_data = pd.DataFrame(data=cl_local).sort_values(by="timestamp", ascending=True).drop(columns=["_id"])
    #print("Historical data fetched from database:")
    #print(db_data)

    if len(db_data) < 10:
        print("Insufficient historical data!")
        return None

    input_dataframe = close_feature_creation(input_dataframe, db_data)
    #print("After close feature creation:")
    #print(input_dataframe)

    input_dataframe.fillna({
        'close_previous_diff': 0.0,
        'rolling_average_3': input_dataframe['close_previous_diff'],
        'rolling_average_5': input_dataframe['rolling_average_3'],
        'rolling_average_10': input_dataframe['rolling_average_5']
    }, inplace=True)

    model_order = ["ticker", "timestamp", "open", "high", "low", "close", "month", "day", "hour", "minute", "year_2022", "year_2023", "year_2024", "close_diff", "close_previous_diff", "rolling_average_log", "rolling_average_3", "rolling_average_5", "rolling_average_10", "year", "APIname"]
    input_dataframe = input_dataframe.reindex(columns=model_order)
    #print("Reordered DataFrame for model input:")
    #print(input_dataframe)

    input_dataframe_scaled = scaler.transform(input_dataframe.drop(columns=["close_diff", "timestamp", "year", "APIname", "ticker"]))
    #print("Scaled input data for predictions:")
    #print(input_dataframe_scaled)

    predictions = model.predict(input_dataframe_scaled)
    input_dataframe["prediction"] = predictions
    #print("Predictions added to DataFrame:")
    #print(input_dataframe)

    database_insert(input_dataframe)
    return input_dataframe

def timestamp_feature_creation(input_dataframe):
    #print("Creating timestamp features...")
    if 'timestamp' not in input_dataframe.columns:
        raise KeyError("'timestamp' column missing in input dataframe")

    input_dataframe['timestamp'] = pd.to_datetime(input_dataframe['timestamp'], unit='s')
    input_dataframe['year'] = input_dataframe['timestamp'].dt.year
    input_dataframe['month'] = input_dataframe['timestamp'].dt.month
    input_dataframe['day'] = input_dataframe['timestamp'].dt.day
    input_dataframe['hour'] = input_dataframe['timestamp'].dt.hour
    input_dataframe['minute'] = input_dataframe['timestamp'].dt.minute
    input_dataframe['year_2022'] = 0
    input_dataframe['year_2023'] = 0
    input_dataframe['year_2024'] = 1
    #print("Timestamp features created:")
    #print(input_dataframe)
    return input_dataframe

def close_feature_creation(input_dataframe, hist_data):
    print("Creating close features...")

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
        input_dataframe['rolling_average_log'] = input_dataframe['rolling_average_3'] = input_dataframe['rolling_average_5'] = input_dataframe['rolling_average_10'] = 0
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

    #print(input_dataframe)
    return input_dataframe


def database_insert(input_data):
    #print("Inserting data into database...")
    last_prediction = collection.find().sort("_id", -1).limit(1)
    lp_dataframe = pd.DataFrame(data=last_prediction).sort_values(by="timestamp", ascending=True).drop(columns=["_id"])
    #print("Last prediction fetched from database:")
    #print(lp_dataframe)

    last_timestamp = lp_dataframe['timestamp'].iloc[0] if not lp_dataframe.empty else None
    input_timestamp = input_data['timestamp'].iloc[0]
    if last_timestamp == input_timestamp:
        print("Duplicate prediction discarded.")
    else:
        input_data = input_data.to_dict(orient="records")
        collection.insert_many(input_data)
        print("Data inserted into database.")

def kafka_output(input_dataframe):
    # Converts predictions for Kafka stream transfer and sends to "analytics-service" module
    json_string = input_dataframe.to_json(orient='records')
    output = json.loads(json_string)
    output[0]['timestamp'] = output[0]['timestamp'] // 1000
    return output

def kafka_pipeline():
    print("Starting Kafka pipeline...")
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
            if prediction_data is not None:
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
