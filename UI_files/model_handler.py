import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from Model.data_preprocessor import read_initial_data, outlier_treatment, clearWeekends, scaled_predict, timelagged, \
    scaled_train
from Model.results import predict_results, anomaly_flag
from UI_files.resource_path import resource_path


def run_model(file_path, new_data, pressure_threshold=-0.3):
    file_path = resource_path(file_path)
    print(f"Running model with file: {file_path}")

    try:
        # 1. Preprocessing
        print("Starting preprocessing...")
        preprocess_data = clearWeekends(new_data)
        print('Cleared weekends')

        # Remove recipe number
        if '18Recept - Receptnummer oven 2' in preprocess_data.columns:
            preprocess_data = preprocess_data.drop(columns=['18Recept - Receptnummer oven 2'])
            print('Dropped recipe number column')
        else:
            print('Recipe number column not found')

        # Make date the index
        preprocess_data['Date'] = pd.to_datetime(preprocess_data['Date'], dayfirst=True)
        preprocess_data = preprocess_data.set_index('Date')
        print('Set date as index')
        print(preprocess_data.head())

        preprocess_data = scaled_predict(preprocess_data)
        print('Scaled data')

        preprocess_data = timelagged(preprocess_data, n_past=6)  # Example value for n_past
        print('Applied time lagging')

        print('Preprocessing done')

        # 2. Predicting with the model
        predictions = predict_results(new_data, preprocess_data)
        print('Predictions done')

        anomaly_predictions = anomaly_flag(predictions)
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
        preprocess_data = clearWeekends(new_data)
        print('Cleared weekends')

        # Remove recipe number
        if '18Recept - Receptnummer oven 2' in preprocess_data.columns:
            preprocess_data = preprocess_data.drop(columns=['18Recept - Receptnummer oven 2'])
            print('Dropped recipe number column')
        else:
            print('Recipe number column not found')

        # Make date the index
        preprocess_data['Date'] = pd.to_datetime(preprocess_data['Date'], dayfirst=True)
        preprocess_data = preprocess_data.set_index('Date')
        print('Set date as index')
        print(preprocess_data.head())

        preprocess_data = outlier_treatment(preprocess_data, pressure_threshold=pressure_threshold, moisture_lower=0,
                                            moisture_upper=15)

        preprocess_data = scaled_train(preprocess_data)
        print('Scaled data')

        preprocess_data = timelagged(preprocess_data, n_past=6)  # Example value for n_past
        print('Applied time lagging')

        print('Preprocessing done')

        # 2. Predicting with the model
        predictions = predict_results(new_data, preprocess_data)
        print('Predictions done')

        anomaly_predictions = anomaly_flag(predictions)
        print('Anomaly detection done')

        print(f'Anomaly list : {anomaly_predictions}')

        return new_data, anomaly_predictions  # returning data to be plotted

    except Exception as e:
        print(f"An error occurred: {e}")
