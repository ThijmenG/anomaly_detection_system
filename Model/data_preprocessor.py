import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import joblib

#Code to remove weekends from the dataset
def clearWeekends(df: pd.DataFrame) -> pd.DataFrame:
    """
    Removes the weekend date from the input dataframe

    Args:
        df (pd.Dataframe): A pandas dataframe to remove weekend dates

    Returns:
        df (pd.Dataframe): A pandas dataframe with the weekend dates removed
    """

    toDrop = []
    for ind, row in df.iterrows():
        date = row["Date"]
        day = date.weekday()

        # Conditions for removal: friday past 23, saturday, sunday before 23
        if day == 4 and date.hour > 23:
            toDrop.append(ind)
        elif day == 5:
            toDrop.append(ind)
        elif day == 6 and date.hour <= 23:
            toDrop.append(ind)

    newDf = df.drop(index = toDrop)

    return newDf

def read_initial_data(df: pd.DataFrame):
    """
    Prepares the initial data to be fed for training and prediction

    Args:
        df (pd.DataFrame): raw dataframe to process

    Returns:
        df (pd.DataFrame): Dataframe with index set, weekends removed, columns filtered and null values filled
    """

    df['Date'] = pd.to_datetime(df['Date'] , dayfirst = True)
    df = clearWeekends(df)
    df = df.set_index('Date',inplace=True)
    df.ffill(inplace=True)

    columns_to_select = ['18BL02PT\PV -  (Bar)','18BL03PT\PV -  (Bar)','18FI02LT01 -  (kg)','18OV01HM01_filtered -  (%)'] #Replace columns needed for filtering
    df = df[columns_to_select]

    return df

def outlier_treatment(df: pd.DataFrame):
    """
    Removes the outliers in the data for training by capping the values to nominal level (use only training data)

    Args:
        df (pd.DataFrame): Dataframe to remove the outliers

    Returns:
        df (pd.DataFrame): Dataframe with capped values
    """

    df.loc[df['18BL02PT\PV -  (Bar)'] < -0.3 , '18BL02PT\PV -  (Bar)'] = -0.3
    df.loc[df['18BL03PT\PV -  (Bar)'] < -0.3 , '18BL03PT\PV -  (Bar)'] = -0.3
    df.loc[df['18FI02LT01 -  (kg)'] > 15 , '18FI02LT01 -  (kg)'] = 15
    df.loc[df['18FI02LT01 -  (kg)'] < 0 , '18FI02LT01 -  (kg)'] = 0
    df.loc[df['18OV01HM01_filtered -  (%)'] > 3.5 , '18OV01HM01_filtered -  (%)'] = 3.5
    df.loc[df['18OV01HM01_filtered -  (%)'] < 2 , '18OV01HM01_filtered -  (%)'] = 2

    return df

def scaled_train(df : pd.DataFrame):
    """
    Scales the training data and stores the scaling model for transforming latest prediction
    Should use this scaler only for training the model

    Args:
        df (pd.DataFrame): Training dataframe for scaling and transforming

    Returns:
        scaled_arr_final (np.array): Scaled prediction array for creating time lagged features (training)
    """

    scaler = MinMaxScaler() #Initializing the scaler
    scaled_arr = scaler.fit_transform(df)

    scaler_filename = "scaler.save" #Name of file used to save the scaling model
    joblib.dump(scaler, scaler_filename)

    scaled_arr_final = scaled_arr.reshape(scaled_arr.shape[0],1,scaled_arr.shape[1]) #Reshaping the training for creating lagged values

    return scaled_arr_final

def scaled_predict(df : pd.DataFrame):
    """
    Scales the prediction data by importing the scaled model
    Should use this scaler only for anomaly detection

    Args:
        df (pd.DataFrame): Prediction dataframe for scaling and transforming

    Returns:
        scaled_arr_final (np.array): Scaled prediction array for creating time lagged features
    """
    
    scaler_filename = 'scaler.save'
    scaler = joblib.load(scaler_filename)

    scaled_arr = scaler.transform(df)
    scaled_arr_final = scaled_arr.reshape(scaled_arr.shape[0],1,scaled_arr.shape[1])

    return scaled_arr_final


def timelagged(rawdata : np.array, n_past : int):
    """
    Creates time lagged features used for training the model and prediction of anomalies
    Used for both training and prediction

    Args:
        rawdata (np.array): Scaled numpt array for conversion into time lagged feature as input to model

    Returns:
        data_X (np.array): Time lagged features from the input dataframe 
        Should be in the shape form (number of rows, number of time lagged considered , 1 , number of columns considered)

    """

    data_X = []

    for i in range(n_past, len(rawdata)):
            data_X.append(rawdata[i - n_past:i, 0:rawdata.shape[1]])
    
    return np.array(data_X)