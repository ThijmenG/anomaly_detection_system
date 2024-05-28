import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from Model.data_preprocessor import read_initial_data, outlier_treatment, clearWeekends, scaled_predict, timelagged, scaled_train
from Model.results import predict_results, anomaly_flag
from Model.model_builder import lstm_model, train_model, plot_model

def run_model(file_path, new_data, pressure_threshold=-0.3):
    print(f"Running model with file: {file_path}")

    try:
        # 1. Preprocessing
        print("Starting preprocessing...")
        preprocess_data = clearWeekends(new_data)
        print('Cleared weekends')

        preprocess_data = read_initial_data(preprocess_data)

        # Remove recipe number
        if '18Recept - Receptnummer oven 2' in preprocess_data.columns:
            preprocess_data = preprocess_data.drop(columns=['18Recept - Receptnummer oven 2'])
            print('Dropped recipe number column')
        else:
            print('Recipe number column not found')

        print('Set date as index')
        print(preprocess_data.head())

        preprocess_data = scaled_predict(preprocess_data, -0.3)
        print('Scaled data')

        preprocess_data = timelagged(preprocess_data, n_past=6)  # Example value for n_past
        print('Applied time lagging')

        print('Preprocessing done')

        # 2. Predicting with the model
        predictions = predict_results(new_data, preprocess_data, -0.3)
        print('Predictions done')

        anomaly_predictions = anomaly_flag(predictions)
        print('Anomaly detection done')
        
        print(f'Anomaly list : {anomaly_predictions}')

        return new_data, anomaly_predictions  # returning data to be plotted

    except Exception as e:
        print(f"An error occurred: {e}")

def train_model(file_path, new_data, pressure_threshold = -0.3):

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
        preprocess_data = read_initial_data(preprocess_data)

        print('Read initial data')
        print(preprocess_data.head())

        preprocess_data = outlier_treatment(preprocess_data, pressure_threshold= pressure_threshold , moisture_upper= 15 , moisture_lower= 0 )

        preprocess_data = scaled_train(preprocess_data, -0.3)
        print('Scaled data')

        preprocess_data = timelagged(preprocess_data, n_past=6)  # Example value for n_past
        print('Applied time lagging')

        print('Preprocessing done')

        model = lstm_model(preprocess_data)

        history = train_model(preprocess_data, model, -0.3)

        fig = plot_model(history)

        return fig  # returning data to be plotted

    except Exception as e:
        print(f"An error occurred: {e}")
