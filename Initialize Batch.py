from audioop import rms
from DeepLearner import *
import matplotlib.pyplot as plt

model_name = "BOT"
Model = Model_Class()

for i in range(8):
    Model.load(model_name+"RATIO"+str(i+1), bias_count=1, input_count=60, hidden_count=8, output_count=5, layer_count=5, activation_values=[4,4,4,4,4,4])

for i in range(2):
    Model.load(model_name+"BINARY"+str(i+1), bias_count=1, input_count=60, hidden_count=16, output_count=1, layer_count=5, activation_values=[4,4,4,4,4,8])
