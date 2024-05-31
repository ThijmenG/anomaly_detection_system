import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from Model.data_preprocessor import read_initial_data, outlier_treatment, clearWeekends, scaled_predict, timelagged, \
    scaled_train
from Model.results import predict_results, anomaly_flag
from Model.model_builder import lstm_model, train_model , plot_model
from UI_files.resource_path import resource_path


def run_model(file_path, new_data, pressure_threshold=-0.3):
    file_path = resource_path(file_path)
    print(f"Running model with file: {file_path}")

    try:
        # 1. Preprocessing
        print("Starting preprocessing...")
        prediction_data = clearWeekends(new_data)
        print('Cleared weekends')

        # Perform Initial Setup
        prediction_data = read_initial_data(prediction_data)
        print('Intial setup complete')

        #Scaling the prediciton values
        preprocess_data = scaled_predict(prediction_data, pressure_threshold)
        print('Scaled data')

        #Creating time lagged inputs
        preprocess_data = timelagged(preprocess_data, n_past=2)  # Example value for n_past
        print('Applied time lagging')

        print('Preprocessing done')

        # 2. Predicting with the model
        predictions = predict_results(prediction_data, preprocess_data, pressure_threshold)
        print('Predictions done')

        anomaly_predictions = anomaly_flag(predictions, pressure_threshold)
        print('Anomaly detection done')

        print(f'Anomaly list : {anomaly_predictions}')

        return new_data, anomaly_predictions  # returning data to be plotted

    except Exception as e:
        print(f"An error occurred: {e}")


def train_model(file_path, new_data, pressure_threshold=-0.3):
    file_path = resource_path(file_path)
    print(f"Running model with file: {file_path}")

    try:
        # 1. Preprocessing
        print("Starting preprocessing...")

        full_data = clearWeekends(new_data)
        print('Cleared weekends')

        # Initial Setup
        full_data = read_initial_data(full_data)
        print('Initial setup done')

        #Outlier Treatment
        preprocess_data = outlier_treatment(full_data, pressure_threshold=pressure_threshold, moisture_upper=15, moisture_lower=0)
        print('Outlier Treatment done')
        
        #Scaling the values
        preprocess_data = scaled_train(preprocess_data, pressure_threshold)
        print('Scaled data')

        #Create time lagged features
        preprocess_data = timelagged(preprocess_data, n_past=2)  # Example value for n_past
        print('Applied time lagging')

        print('Preprocessing done')

        # 2. Training the model
        model = lstm_model(preprocess_data)
        print('Predictions done')

        history = train_model(preprocess_data, model, pressure_threshold)
        print('Training done')

        fig = plot_model(history)

        return fig  # returning the training figure for visual inspection

    except Exception as e:
        print(f"An error occurred: {e}")
