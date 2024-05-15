import tensorflow as tf
import keras
from keras.layers import Input, Dropout, Dense, LSTM, TimeDistributed, RepeatVector
from keras.models import Model
from keras import regularizers
import numpy as np


def lstm_model(ip_arr_arr : np.array):
    """
    Initializing a LSTM model with Encoder-Decoder architecture

    Args:
        ip_arr (np.array): An input numpy array that is used for training will be used to create a architecture

    Returns:
        model (keras.models): A model object without any weights
    """
    
    ip_arr = ip_arr.reshape((ip_arr.shape[0], ip_arr.shape[1], ip_arr.shape[3])) #Reshaping the input array to match the input dimensions of the model
    inputs = Input(shape = (ip_arr.shape[1], ip_arr.shape[2])) #Initializing the input size for the model

    L1 = LSTM(16 , activation = 'relu' , return_sequences= True , kernel_regularizer=regularizers.l2(0.00))(inputs) #Model architecture
    L2 = LSTM(4 , activation='relu' , return_sequences=False)(L1)
    L3 = RepeatVector(ip_arr.shape[1])(L2)
    L4 = LSTM(4 , activation='relu' , return_sequences=True)(L3)
    L5 = LSTM(16 , activation='relu' , return_sequences=True)(L4)

    output = TimeDistributed(Dense(ip_arr.shape[2]))(L5)
    model = Model(inputs = inputs , outputs = output)

    return model

