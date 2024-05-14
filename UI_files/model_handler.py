import numpy as np
import matplotlib.pyplot as plt


def run_model(file_path, new_data):
    print(f"Running model with file: {file_path}")

    #TODO
    #1. preproccesing
    processed_data = new_data

    #2. predicting with the model
    # Placeholder: Generate some data to plot
    x = np.linspace(0, 10, 100)
    y = np.sin(x)

    predictions = (x, y)

    #3. postprocessing
    #4. return the predictions
    #5. retrain the model with the new data



    # Normally you would have your model process the file and DataFrame and generate data
    return processed_data, predictions  # returning data to be plotted
