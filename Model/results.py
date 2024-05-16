import numpy as np
import pandas as pd
import keras as keras
import matplotlib.pyplot as plt

def predict_results(original_df : pd.DataFrame, scaled_arr : np.array):
    """
    Given the original dataframe and scaled input form, it predicts the results and returns a dataframe with error

    Args:
        original_df (pd.DataFrame) : Original dataframe to be checked for anomaly
        scaled_arr (np.array) : Scaled input array for model

    Returns:
        error_df (pd.DataFrame) : Difference in model prediction with respect to original dataframe
    """

    model = keras.models.load_model(f"model_1.keras") #Importing the trained model (Change the name according to the saved model)
    scaled_arr = scaled_arr.reshape((scaled_arr.shape[0], scaled_arr.shape[1], scaled_arr.shape[3])) #Reshaping according to the model input required

    predictions = model.predict(scaled_arr)

    error = np.mean(np.abs(scaled_arr - predictions), axis = 2) #Error calculation column wise and taking the mean
    calculated_error = np.zeros(original_df.shape[0])
    for i in range(len(error)):
        for j in range(error.shape[1]):
            calculated_error[i+j] += error[i , j]
    for i in range(len(calculated_error)):
        calculated_error[i] = calculated_error[i]/min(i+1 , 6 , len(calculated_error) - i) #loop for error calculation for rows (time frames)

    error_df = pd.DataFrame({'Error':calculated_error})
    error_df.set_index(original_df.index, inplace=True)

    return error_df

def anomaly_flag(df : pd.DataFrame):
    """
    Given a dataframe with error from model, returns anamoly flag based on two parameters(AE: Average Error & DC: Danger Coefficient)
    
    Args:
        df (df.DataFrame): Dataframe with error from model
    
    Returns:
        df (df.DataFrame): Dataframe with calculated parameters (AE & DC) and anamoly flag
    """

    df['AE'] = df['Error'].rolling(6 , min_periods=1).sum() / 6 #Taking a rolling mean of error based on last 6 values
    df['flag'] = np.where(df['Error'] > 0.27, 1, 0)
    df['DC'] = df['flag'].rolling(6 , min_periods=1).sum() / 6 #Taking a rolling mean of error flag based on last 6 values
    df.drop('flag', axis=1, inplace=True)

    df['Anamoly'] = np.where((df['DC'] > 0.66) & (df['AE'] > 0.23), 1, 0) #Change the threshold for anomaly flag

    return df

def plot_anomaly(original_df : pd.DataFrame, flag_df : pd.DataFrame):
    """
    Plot the pressure sensor value with anomaly flag

    Args:
        original_df (pd.DataFrame) : Original dataframe that is used for anomaly detection
        flag_df (pd.DataFrame) : Dataframe with calculated parameters (AE & DC) and anamoly flag

    Returns:
        fig (matplotlib.figure) : Figure with pressure sensor values plotted and anomalies as red vertical lines
    """

    indices = flag_df[flag_df['Anamoly'] == 1].index #Getting the time values where anomalies arised

    # defining plot size
    fig = plt.figure(figsize = (15, 15)) #Change the figure size

    plt.plot(original_df['18BL02PT\\PV -  (Bar)'])

    for date in indices:
        plt.axvline(x = date, color = 'r',label='Anomaly') #Looping and plotting for each anomaly time value

    plt.legend(['Pressure','Anamolies'], fontsize="10" , bbox_to_anchor = (0.4, 1) , ncol=2)

    plt.xlabel("Timeline")
    plt.ylabel("Pressure Sensor 2 (Bar)")

    return fig