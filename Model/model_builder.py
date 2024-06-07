import tensorflow as tf
import keras
from keras.layers import Input, Dropout, Dense, LSTM, TimeDistributed, RepeatVector
from keras.models import Model
from keras import regularizers
import numpy as np
import matplotlib.pyplot as plt
from UI_files.resource_path import resource_path


def lstm_model(ip_arr: np.array):
    """
    Initializing a LSTM model with Encoder-Decoder architecture

    Args:
        ip_arr (np.array): An input numpy array that is used for training will be used to create a architecture

    Returns:
        model (keras.models): A model object without any weights
    """

    ip_arr = ip_arr.reshape((ip_arr.shape[0], ip_arr.shape[1],
                             ip_arr.shape[3]))  # Reshaping the input array to match the input dimensions of the model
    inputs = Input(shape=(ip_arr.shape[1], ip_arr.shape[2]))  # Initializing the input size for the model

    L1 = LSTM(48, activation='relu', return_sequences=True, kernel_regularizer=regularizers.l2(0.00))(inputs)  # Model architecture
    L2 = LSTM(36, activation='relu', return_sequences=False)(L1)
    L3 = RepeatVector(ip_arr.shape[1])(L2)
    L4 = LSTM(36, activation='relu', return_sequences=True)(L3)
    L5 = LSTM(48, activation='relu', return_sequences=True)(L4)

    output = TimeDistributed(Dense(ip_arr.shape[2]))(L5)
    model = Model(inputs=inputs, outputs=output)

    return model


def train_model(ip_arr: np.array, model: keras.src.models.functional.Functional, pressure_threshold: float):
    """
    Training the model using the prepared data
    Requires data with lagged input features

    Args:
        ip_arr (np.array): Input array with lagged input features for training the model

    Returns:
        model (keras) : Model is saved in the path specified
        history (tensorflow.python.keras.callbacks.History) : History from training the model
    """

    ip_arr = ip_arr.reshape((ip_arr.shape[0], ip_arr.shape[1], ip_arr.shape[3]))  # Reshaping the input array to match the input dimensions of the model

    optimizers = keras.optimizers.Adam(learning_rate=0.001)
    model.compile(optimizer=optimizers, loss='mae')  # The optimizer and loss function can be changed

    epochs_n = 100  # Parameters can be finetuned
    batch_n = 128

    pressure_threshold_str = str(pressure_threshold)[1:].replace('.', '_')

    model_save_path = resource_path(rf"Source_file\model_{pressure_threshold_str}.keras")
    
    history = model.fit(ip_arr, ip_arr, epochs=epochs_n, batch_size=batch_n, validation_split=0.05, shuffle = True).history
    model.save(model_save_path)  # Location for saving the model file

    return history


def plot_model(history):
    """
    Plots the training history of the model

    Args:
        history (tensorflow.python.keras.callbacks.History) : History from training the model

    Returns:
        fig (Figure) : Graph of the training history

    """

    fig, ax = plt.subplots(figsize=(14, 6), dpi=100)
    ax.plot(history['loss'], 'b', label='Train', linewidth=2)
    ax.plot(history['val_loss'], 'r', label='Validation', linewidth=2)
    ax.set_title('Model Loss')
    ax.set_xlabel('Epochs')
    ax.set_ylabel('Loss (MAE)')
    ax.legend(loc='upper right')

    return fig
