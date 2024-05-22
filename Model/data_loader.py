import pandas as pd

def CSVstartChecker(file_path: str):
    """
    Reads a file and returns the number of the first line contining "DateTime,TagName,Value", which is where the time indexed data starts.

    Args:
        file_path (srt): The path to the file to have its start line checked

    Returns:
        int: Line number of the first line containing "DateTime,TagName,Value"
    """
    with open(file_path) as f:
        lines = f.readlines()
        for i in range(len(lines)):
            if lines[i].startswith("DateTime,TagName,Value"):
                return i

def CSVsplitterMerger(df: pd.DataFrame):
    """
    Takes a raw import as input and returns a dataframe with data horizontally merged on tag and vertically on date and time

    Args:
        df (pd.DataFrame): Raw dataframe to process

    Returns:
        df (pd.DataFrame): Dataframe containing the merged data
    """
    tags = pd.unique(df["TagName"]) # List of tags in the export
    frames = []
    for tag in tags: # Separates each tag into a different dataframe
        frame = df.loc[df["TagName"]==tag]
        frame = frame.rename(columns = {"Value":tag})
        frame = frame.drop(columns = ["TagName"])

        # Fix the numerical values to use standard decimal marker and convert to float
        frame[tag] = frame[tag].replace(to_replace={",":"."}, regex=True)
        frame[tag] = pd.to_numeric(frame[tag])

        frames.append(frame)

    df_final = frames[0]
    if len(frames)>1: # Check if there are multiple frames which need to be merged
        for i in range(1,len(frames)): # Merges all dataframes together on date and time
            df_final = df_final.merge(frames[i], on = "DateTime")

    return df_final

def dateTimeFix(df: pd.DataFrame):
    """
    Fixes the date column name and the date format to ensure proper data processing.

    Args:
        df (pd.DataFrame): Dataframe with date column in original state

    Returns:
        df (pd.DataFrame): Dataframe with the dates and column name fixed
    """
    df = df.rename(columns = {"DateTime":"Date"}) # Fix the date column tag

    replDict = {" jan ": "-01-",
            " feb ": "-02-",
            " mrt ": "-03-",
            " apr ": "-04-",
            " mei ": "-05-",
            " jun ": "-06-",
            " jul ": "-07-",
            " aug ": "-08-",
            " sep ": "-09-",
            " okt ": "-10-",
            " nov ": "-11-",
            " dec ": "-12-"}
    df["Date"] = df["Date"].replace(to_replace=replDict, regex=True) # Standardize the date
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True) # Turn the datetimes into correct type

    return df

def checkData(df: pd.DataFrame):
    """
    Checks if all required columns are present in the dataframe

    Args:
        df (pd.DataFrame): Dataframe to be checked

    Returns:
        bool: Wether all columns have been found
    """
    reqColumns = ['18BL02PT\\PV -  (Bar)','18BL03PT\\PV -  (Bar)','18FI02LT01 -  (kg)','18OV01HM01_filtered -  (%)']
    for col in reqColumns:
        if col not in df.columns:
            return False
    return True

def data_loader(file_path: str):
    """
    Load data from a CSV or Excel file and return it as a DataFrame.

    Parameters:
    file_path (str): The path to the file to be loaded.

    Returns:
    pd.DataFrame: The loaded data as a DataFrame.

    Raises:
    ValueError: If the file format is not supported.
    """
    if file_path.endswith('.csv'):
        startLine = CSVstartChecker(file_path)
        raw = pd.read_csv(file_path, skiprows=startLine)
        df = CSVsplitterMerger(raw)
    elif file_path.endswith('.xlsx'):
        testDf = pd.read_excel(file_path, skiprows=range(5)) # Read everything including the sensor types
        emptyRow = testDf.isnull().all(axis=1) # Find where the sensor preamble ends
        n = testDf[emptyRow].index[0] # Mark the number of rows in the sensor preamble

        # Read the actual data
        df = pd.read_excel(file_path, skiprows=range(7+n))
        df = df.rename(columns={"Unnamed: 1":"DateTime"})
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    else:
        raise ValueError("Unsupported file format. Please select a CSV or Excel file.")
    
    df = dateTimeFix(df)
    columnCheck = checkData(df)
    if not columnCheck:
        raise ValueError("Not all required columns are present in the dataset.")
    return df


