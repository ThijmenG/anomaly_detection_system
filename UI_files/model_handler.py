import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta


def run_model(file_path, new_data):
    print(f"Running model with file: {file_path}")

    #TODO
    #1. preproccesing
    processed_data = new_data

    #2. predicting with the model
    # Placeholder: Generate some data to plot
    x = np.linspace(0, 10, 100)
    y = np.sin(x)

    # Create a list of three datetime objects
    predictions = [datetime(2024, 4, 21, 23, 18),
                   datetime(2024, 4, 21, 23, 18) + timedelta(days=1),
                   datetime(2024, 4, 21, 23, 18) + timedelta(days=2)]

    #3. postprocessing
    #4. return the predictions
    #5. retrain the model with the new data



    # Normally you would have your model process the file and DataFrame and generate data
    return processed_data, predictions  # returning data to be plotted
