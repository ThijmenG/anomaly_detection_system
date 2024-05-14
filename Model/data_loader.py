import pandas as pd

def data_loader(file_path):
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
        df = pd.read_csv(file_path)
    elif file_path.endswith('.xlsx'):
        df = pd.read_excel(file_path)
    else:
        raise ValueError("Unsupported file format. Please select a CSV or Excel file.")

    return df
