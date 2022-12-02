import matplotlib.pyplot as plt
from DeepLearner import *
from decimal import *
from time import *
import requests

getcontext().prec = 64

model_name = input("Model name: ")

Trade_Model = Model_Class()
Trade_Model.load(model_name, min_diff=0.00000001, learning_rate=0.000001, cycles=5)

Trade_Data_test = Data_Class()

Trade_Data_train = Data_Class()
Trade_Data_validate = Data_Class()

Trade_Data_uncertainty = Data_Class()


url = "http://127.0.0.1:8080"

request_register = requests.get(url + "/register", json = {"startBalanceA" : 10.0, "startBalanceB" : 10.0}).json()

userID = request_register["userID"]

predicted_count = 10

average_size = 6

start_flag = True



x_values = [i for i in range(Trade_Model.input_count+predicted_count)]

request_getHistoricPrices = requests.get(url + "/getHistoricPrices", json = {"userID" : userID, "onlyRecent" : False}).json()
previous_rates = [Decimal(i) for i in request_getHistoricPrices["avgPrice"]]

while True:
    request_getBalance = requests.get(url + "/getBalance", json = {"userID" : userID}).json()
    
    balance_A = Decimal(request_getBalance["balanceA"])
    balance_B = Decimal(request_getBalance["balanceB"])
    
    request_getHistoricPrices = requests.get(url + "/getHistoricPrices", json = {"userID" : userID, "onlyRecent" : True}).json()
    previous_rates += [Decimal(i) for i in request_getHistoricPrices["avgPrice"]]
    
    unit_rate = previous_rates[-1]

    moving_average_previous_rates = [sum(previous_rates[i:i+average_size])/Decimal(average_size) for i in range(len(previous_rates)-average_size+1)]
    
    change_moving_average_rates = [moving_average_previous_rates[i+1]/moving_average_previous_rates[i] for i in range(len(moving_average_previous_rates)-1)]
    
    
    
    Trade_Data_test.load(input_values=change_moving_average_rates, target_values=[], stream=True, shift_count=1)
    
    Trade_Model.recursive_test(Trade_Data_test, loop_count=predicted_count, feedback_count=5, pivot_value=1, auto_adjust=False)



    compounded_multiplier = Decimal(1)
    compounded_moving_change = []
    
    for multiplier in Trade_Model.recursive_output_values:
        compounded_multiplier *= multiplier

        compounded_moving_change.append(compounded_multiplier-Decimal(1))
        
    compounded_actual_change = []

    for change in compounded_moving_change:
        compounded_actual_change.append((moving_average_previous_rates[-1]*(change+Decimal(1)))/unit_rate-Decimal(1))



    uncertainty_values_lower = [Decimal(0) for i in range(predicted_count)]
    uncertainty_values_upper = [Decimal(0) for i in range(predicted_count)]
    
    for h in range(0, len(change_moving_average_rates)-Trade_Model.input_count+1-predicted_count):
        Trade_Data_uncertainty.load(input_values=change_moving_average_rates[h:h+Trade_Model.input_count], target_values=[], stream=False, shift_count=Trade_Model.input_count)
        
        Trade_Model.recursive_test(Trade_Data_uncertainty, loop_count=predicted_count, feedback_count=1, pivot_value=1, auto_adjust=False)
        
        
        
        compounded_multiplier_real = Decimal(1)
        compounded_multiplier_uncertainty = Decimal(1)
        
        for i in range(predicted_count):
            compounded_multiplier_real *= change_moving_average_rates[Trade_Model.input_count+h+i]
            compounded_multiplier_uncertainty *= Trade_Model.recursive_output_values[i]
            
            uncertainty_level = compounded_multiplier_real-compounded_multiplier_uncertainty
            
            if uncertainty_level < 0:
                uncertainty_values_lower[i] += uncertainty_level/Decimal(len(change_moving_average_rates)-Trade_Model.input_count+1-predicted_count)
            if uncertainty_level > 0:
                uncertainty_values_upper[i] += uncertainty_level/Decimal(len(change_moving_average_rates)-Trade_Model.input_count+1-predicted_count)
    
    
    
    compounded_moving_change_lower = [compounded_moving_change[i]+uncertainty_values_lower[i] for i in range(predicted_count)]
    compounded_moving_change_upper = [compounded_moving_change[i]+uncertainty_values_upper[i] for i in range(predicted_count)]
    
    compounded_actual_change_lower = [compounded_actual_change[i]+uncertainty_values_lower[i] for i in range(predicted_count)]
    compounded_actual_change_upper = [compounded_actual_change[i]+uncertainty_values_upper[i] for i in range(predicted_count)]
    
    
    
    y_values_average = moving_average_previous_rates[-Trade_Model.input_count:]
    y_values_lower = []
    y_values_upper = []
    
    for i in range(predicted_count):
        y_values_average.append(moving_average_previous_rates[-1]*(compounded_moving_change[i]+Decimal(1)))
        y_values_lower.append(moving_average_previous_rates[-1]*(compounded_moving_change_lower[i]+Decimal(1)))
        y_values_upper.append(moving_average_previous_rates[-1]*(compounded_moving_change_upper[i]+Decimal(1)))
            
            

    target_proportion_A = Decimal(0)
    target_proportion_B = Decimal(0)
    
    for i in range(predicted_count):
        upper_lower_diff = (compounded_actual_change_upper[i]-compounded_actual_change_lower[i])
            
        temp_proportion_A = compounded_actual_change_upper[i]/upper_lower_diff
        temp_proportion_B = compounded_actual_change_lower[i]/upper_lower_diff
        
        if temp_proportion_A > 1 or temp_proportion_B > 0:
            temp_proportion_A = Decimal(1)
            temp_proportion_B = Decimal(0)
        if temp_proportion_B < -1 or temp_proportion_A < 0:
            temp_proportion_A = Decimal(0)
            temp_proportion_B = Decimal(1)
        
        target_proportion_A += abs(temp_proportion_A)/Decimal(predicted_count)
        target_proportion_B += abs(temp_proportion_B)/Decimal(predicted_count)
        
    
    
    request_getValue = requests.get(url + "/getValue", json = {"userID" : userID}).json()
    
    value_A = Decimal(request_getValue["valueA"])
    value_B = Decimal(request_getValue["valueB"])
    
    value_total = value_A + value_B
    
    actual_proportion_A = value_A/value_total
    actual_proportion_B = value_B/value_total
    
    if actual_proportion_A == 0:
        proportion_change_A = Decimal(0)
    else:
        proportion_change_A = Decimal(1)-target_proportion_A/actual_proportion_A
    if actual_proportion_B == 0:
        proportion_change_B = Decimal(0)
    else:
        proportion_change_B = Decimal(1)-target_proportion_B/actual_proportion_B
    

    desired_price = sum(y_values_average[-predicted_count:])/Decimal(predicted_count)
    
    
    if proportion_change_A <= 0:
        order_data = {"userID" : userID,
                      "ask" : False,
                      "unitPrice" : float(desired_price),
                      "quantity" : float((balance_B*(Decimal(1)-proportion_change_B))/desired_price)}
    if proportion_change_B <= 0:
        order_data = {"userID" : userID,
                      "ask" : True,
                      "unitPrice" : float(desired_price),
                      "quantity" : float(balance_A*(Decimal(1)-proportion_change_A))}
    
    request_placeOrder = requests.post(url + "/placeOrder", json = order_data).json()
    

    print("Target proportion of A: " + str(float(target_proportion_A)))
    print("Target proportion of B: " + str(float(target_proportion_B)))
    print("Value of A: " + str(float(value_A)))
    print("Value of B: " + str(float(value_B)))
    print("Total value: " + str(float(value_total)))
    print("\n")
    
    
    

    
    
    
    input_values_train = change_moving_average_rates[int(len(change_moving_average_rates)/2)+Trade_Model.input_count:]
    input_values_validate = change_moving_average_rates[:int(len(change_moving_average_rates)/2)]
    
    Trade_Data_train.load(input_values=input_values_train, target_values=[], stream=True, shift_count=1)
    Trade_Data_validate.load(input_values=input_values_validate, target_values=[], stream=True, shift_count=1)
    
    Trade_Model.train(Trade_Data_train, Trade_Data_validate)
    Trade_Model.save()
    
    if len(previous_rates) > 600:
        previous_rates = previous_rates[-600:]