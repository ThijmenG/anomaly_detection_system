import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from Model.data_preprocessor import read_initial_data, outlier_treatment, clearWeekends, scaled_predict, timelagged
from Model.results import predict_results, anomaly_flag, plot_anomaly


def run_model(file_path, new_data, pressure_threshold = -0.3, moisture_upper = 0, moisture_lower = 5):
    print(f"Running model with file: {file_path}")

    #TODO
    #1. preproccesing
    preprocess_data = clearWeekends(new_data)
    preprocess_data = scaled_predict(preprocess_data)
    preprocess_data = timelagged(preprocess_data)

    #2. predicting with the model

    predictions = predict_results(preprocess_data)
    anomaly_predictions = anomaly_flag(predictions)


    predictions = [datetime(2024, 4, 21, 23, 18),
                   datetime(2024, 4, 21, 23, 18) + timedelta(days=1),
                   datetime(2024, 4, 21, 23, 18) + timedelta(days=2)]

    #3. postprocessing
    #4. return the predictions
    #5. retrain the model with the new data



    # Normally you would have your model process the file and DataFrame and generate data
    return new_data, anomaly_predictions  # returning data to be plotted

def train_model():
    return
