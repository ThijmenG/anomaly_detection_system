import pandas as pd
import os
from UI_files.resource_path import resource_path

def CSVstartChecker(file_path: str):
    with open(file_path) as f:
        lines = f.readlines()
        for i in range(len(lines)):
            if lines[i].startswith("DateTime,TagName,Value"):
                return i

def CSVsplitterMerger(df: pd.DataFrame):
    tags = pd.unique(df["TagName"])
    frames = []
    for tag in tags:
        frame = df.loc[df["TagName"] == tag]
        frame = frame.rename(columns={"Value": tag})
        frame = frame.drop(columns=["TagName"])
        frame[tag] = frame[tag].replace(to_replace={",": "."}, regex=True)
        frame[tag] = pd.to_numeric(frame[tag])
        frames.append(frame)

    df_final = frames[0]
    if len(frames) > 1:
        for i in range(1, len(frames)):
            df_final = df_final.merge(frames[i], on="DateTime")
    return df_final

def dateTimeFix(df: pd.DataFrame):
    df = df.rename(columns={"DateTime": "Date"})
    replDict = {
        " jan ": "-01-", " feb ": "-02-", " mrt ": "-03-", " apr ": "-04-",
        " mei ": "-05-", " jun ": "-06-", " jul ": "-07-", " aug ": "-08-",
        " sep ": "-09-", " okt ": "-10-", " nov ": "-11-", " dec ": "-12-"
    }
    df["Date"] = df["Date"].replace(to_replace=replDict, regex=True)
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)
    return df

def checkData(df: pd.DataFrame):
    reqColumns = [
        '18BL02PT\\PV -  (Bar)', '18BL03PT\\PV -  (Bar)',
        '18FI02LT01 -  (kg)', '18OV01HM01_filtered -  (%)'
    ]
    for col in reqColumns:
        if col not in df.columns:
            return False
    return True

def data_loader(file_path: str):
    file_path = resource_path(file_path)
    print(file_path)
    if file_path.endswith('.csv'):
        startLine = CSVstartChecker(file_path)
        raw = pd.read_csv(file_path, skiprows=startLine)
        df = CSVsplitterMerger(raw)
    elif file_path.endswith('.xlsx'):
        print('gets to xlsx')
        try:
            testDf = pd.read_excel(file_path, skiprows=range(5), engine='openpyxl')
            print('Initial DataFrame loaded:')
            print(testDf.head())

            emptyRow = testDf.isnull().all(axis=1)
            n = testDf[emptyRow].index[0]
            print(f'First completely empty row index: {n}')

            df = pd.read_excel(file_path, skiprows=range(7 + n), engine='openpyxl')
            df = df.rename(columns={"Unnamed: 1": "DateTime"})
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
            print('Processed DataFrame:')
            print(df.head())
        except Exception as e:
            print(f'Error reading Excel file: {e}')
            raise
    else:
        raise ValueError("Unsupported file format. Please select a CSV or Excel file.")

    df = dateTimeFix(df)
    columnCheck = checkData(df)
    if not columnCheck:
        raise ValueError("Not all required columns are present in the dataset.")
    return df
