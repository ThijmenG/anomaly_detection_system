import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import joblib
import os
from UI_files.resource_path import resource_path

def clearWeekends(df: pd.DataFrame) -> pd.DataFrame:

    df['Date'] = pd.to_datetime(df['Date'] , dayfirst = True)
    toDrop = []
    for ind, row in df.iterrows():
        date = row["Date"]
        day = date.weekday()
        if day == 4 and date.hour > 23:
            toDrop.append(ind)
        elif day == 5:
            toDrop.append(ind)
        elif day == 6 and date.hour <= 23:
            toDrop.append(ind)
    newDf = df.drop(index=toDrop)
    return newDf

def read_initial_data(df: pd.DataFrame):

    df.set_index('Date', inplace=True)
    df.ffill(inplace=True)
    columns_to_select = ['18BL02PT\PV -  (Bar)', '18BL03PT\PV -  (Bar)', '18FI02LT01 -  (kg)', '18OV01HM01_filtered -  (%)']
    df = df[columns_to_select]
    return df

def outlier_treatment(df: pd.DataFrame, pressure_threshold: float):
    df.loc[df['18BL02PT\PV -  (Bar)'] < pressure_threshold, '18BL02PT\PV -  (Bar)'] = pressure_threshold
    df.loc[df['18BL03PT\PV -  (Bar)'] < pressure_threshold, '18BL03PT\PV -  (Bar)'] = pressure_threshold
    df.loc[df['18FI02LT01 -  (kg)'] > 15, '18FI02LT01 -  (kg)'] = 15
    df.loc[df['18FI02LT01 -  (kg)'] < 0, '18FI02LT01 -  (kg)'] = 0
    df.loc[df['18OV01HM01_filtered -  (%)'] > 4, '18OV01HM01_filtered -  (%)'] = 4
    df.loc[df['18OV01HM01_filtered -  (%)'] < 2, '18OV01HM01_filtered -  (%)'] = 2
    return df

def scaled_train(df: pd.DataFrame, pressure_threshold: float):

    scaler = MinMaxScaler()
    scaled_arr = scaler.fit_transform(df)
    pressure_threshold_str = str(pressure_threshold)[1:].replace('.', '_')
    scaler_filename = resource_path(rf"Source_file\trained_scaler\scaler_{pressure_threshold_str}.save")
    joblib.dump(scaler, scaler_filename)
    scaled_arr_final = scaled_arr.reshape(scaled_arr.shape[0], 1, scaled_arr.shape[1])
    return scaled_arr_final

def scaled_predict(df: pd.DataFrame, pressure_threshold : float):

    pressure_threshold_str = str(pressure_threshold)[1:].replace('.', '_')
    scaler_filename = resource_path(rf"Source_file\trained_scaler\scaler_{pressure_threshold_str}.save")

    print('Scaler file name:', scaler_filename)

    if not os.path.isfile(scaler_filename):
        print(f"Scaler file does not exist: {scaler_filename}")
    else:
        try:
            scaler = joblib.load(scaler_filename)
            print('Scaler loaded')
            scaled_arr = scaler.transform(df)
            scaled_arr_final = scaled_arr.reshape(scaled_arr.shape[0], 1, scaled_arr.shape[1])
            return scaled_arr_final
        except FileNotFoundError as fnf_error:
            print(f"File not found error: {fnf_error}")
        except IOError as io_error:
            print(f"IO error: {io_error}")
        except Exception as e:
            print(f"Failed to load scaler: {e}")

def timelagged(rawdata: np.array, n_past: int):
    data_X = []
    for i in range(n_past, len(rawdata)):
        data_X.append(rawdata[i - n_past:i, 0:rawdata.shape[1]])
    return np.array(data_X)
