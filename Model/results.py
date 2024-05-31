import numpy as np
import pandas as pd
import keras as keras
import matplotlib.pyplot as plt
from UI_files.resource_path import resource_path


def predict_results(original_df: pd.DataFrame, scaled_arr: np.array, pressure_threshold: float):
    """
    Given the original dataframe and scaled input form, it predicts the results and returns a dataframe with error

    Args:
        original_df (pd.DataFrame): Original dataframe to be checked for anomaly
        scaled_arr (np.array): Scaled input array for model
        pressure_threshold (float): Threshold for pressure used to differentiate models

    Returns:
        error_df (pd.DataFrame): Difference in model prediction with respect to original dataframe
    """

    pressure_threshold_str = str(pressure_threshold)[1:].replace('.', '_')
    model_path = resource_path(f"Model/model_{pressure_threshold_str}.keras")  # Importing the trained model

    model = keras.models.load_model(model_path)
    scaled_arr = scaled_arr.reshape((scaled_arr.shape[0], scaled_arr.shape[1],
                                     scaled_arr.shape[3]))  # Reshaping according to the model input required

    predictions = model.predict(scaled_arr)

    error = np.mean(np.abs(scaled_arr - predictions), axis=2)  # Error calculation column wise and taking the mean
    calculated_error = np.zeros(original_df.shape[0])
    for i in range(len(error)):
        for j in range(error.shape[1]):
            calculated_error[i + j] += error[i, j]
    for i in range(len(calculated_error)):
        calculated_error[i] = calculated_error[i] / min(i + 1, 6,
                                                        len(calculated_error) - i)  # loop for error calculation for rows (time frames)

    error_df = pd.DataFrame({'Error': calculated_error})
    error_df.set_index(original_df.index, inplace=True)

    return error_df


def anomaly_flag(df: pd.DataFrame):
    """
    Given a dataframe with error from model, returns anomaly flag based on two parameters (AE: Average Error & DC: Danger Coefficient)

    Args:
        df (pd.DataFrame): Dataframe with error from model

    Returns:
        df (pd.DataFrame): Dataframe with calculated parameters (AE & DC) and anomaly flag
    """

    df['AE'] = df['Error'].rolling(6, min_periods=1).sum() / 6  # Taking a rolling mean of error based on last 6 values
    df['flag'] = np.where(df['Error'] > 0.27, 1, 0)
    df['DC'] = df['flag'].rolling(6,
                                  min_periods=1).sum() / 6  # Taking a rolling mean of error flag based on last 6 values
    df.drop('flag', axis=1, inplace=True)

    df['Anomaly'] = np.where((df['DC'] > 0.66) & (df['AE'] > 0.23), 1, 0)  # Change the threshold for anomaly flag

    indices = df[df['Anomaly'] == 1].index  # Getting the time values where anomalies arose

    return indices
