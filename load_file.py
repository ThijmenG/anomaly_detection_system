import pandas as pd
from tkinter import filedialog, messagebox

""" here can the loading logic be implemented """

def load_file():
    # Open the file chooser dialog to select a CSV or Excel file
    filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")])
    if not filepath:
        return

    try:
        #TODO is this the correct loading logic?
        # Load the file into a DataFrame
        if filepath.endswith('.csv'):
            df = pd.read_csv(filepath)
        else:
            df = pd.read_excel(filepath)

        # Check for specific columns (example: 'Name', 'Age')
        required_columns = []
        if all(column in df.columns for column in required_columns):
            messagebox.showinfo("Success", "File loaded successfully and all required columns are present.")
        else:
            missing = [column for column in required_columns if column not in df.columns]
            messagebox.showerror("Error", "Missing columns: " + ", ".join(missing))

        return filepath, df  # Return the filepath when a file is successfully loaded

    except Exception as e:
        messagebox.showerror("Error", "Failed to load the file.\n" + str(e))