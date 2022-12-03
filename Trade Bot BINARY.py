import matplotlib.pyplot as plt
from DeepLearner import *
from decimal import *
from time import *
import requests

getcontext().prec = 64

model_name = input("Model name: ")

Trade_Model = Model_Class()
Trade_Model.load(model_name, min_diff=0.00000001, learning_rate=0.0003, cycles=5)

Trade_Data_test = Data_Class()

Trade_Data_train = Data_Class()
Trade_Data_validate = Data_Class()


url = "http://127.0.0.1:8080"

request_register = requests.get(url + "/register", json = {"startBalanceA" : 100.0, "startBalanceB" : 100.0}).json()

userID = request_register["userID"]

average_size = 6



request_getHistoricPrices = requests.get(url + "/getHistoricPrices", json = {"userID" : userID, "onlyRecent" : False}).json()
previous_rates = [Decimal(i) for i in request_getHistoricPrices["avgPrice"]]



request_getBalance = requests.get(url + "/getBalance", json = {"userID" : userID}).json()

last_balance_A = Decimal(request_getBalance["balanceA"])

request_getValue = requests.get(url + "/getValue", json = {"userID" : userID}).json()

start_flag = True

action_values = []

while True:
    request_getBalance = requests.get(url + "/getBalance", json = {"userID" : userID}).json()
    
    balance_A = Decimal(request_getBalance["balanceA"])
    balance_B = Decimal(request_getBalance["balanceB"])
    
    request_getHistoricPrices = requests.get(url + "/getHistoricPrices", json = {"userID" : userID, "onlyRecent" : True}).json()
    previous_rates += [Decimal(i) for i in request_getHistoricPrices["avgPrice"]]
    
    unit_rate = previous_rates[-1]

    moving_average_previous_rates = [sum(previous_rates[i:i+average_size])/Decimal(average_size) for i in range(len(previous_rates)-average_size+1)]
    
    change_moving_average_rates = [moving_average_previous_rates[i+1]/moving_average_previous_rates[i] for i in range(len(moving_average_previous_rates)-1)]
    
    
    
    
    Trade_Data_test.load(input_values=change_moving_average_rates[-Trade_Model.input_count:], target_values=[], stream=True, shift_count=1)
    
    Trade_Model.test(Trade_Data_test)


    
    request_getValue = requests.get(url + "/getValue", json = {"userID" : userID}).json()
    
    value_A = Decimal(request_getValue["valueA"])
    value_B = Decimal(request_getValue["valueB"])
    
    value_total = value_A + value_B
    
    
    if Trade_Model.output_values[-1] >= 0.5:
        order_data = {"userID" : userID,
                      "ask" : False,
                      "unitPrice" : float(unit_rate),
                      "quantity" : float(balance_B/unit_rate)}
    if Trade_Model.output_values[-1] < 0.5:
        order_data = {"userID" : userID,
                      "ask" : True,
                      "unitPrice" : float(unit_rate),
                      "quantity" : float(balance_A)}
    
    request_placeOrder = requests.post(url + "/placeOrder", json = order_data).json()
    
    

    print("Action: " + str(Trade_Model.output_values[-1]))
    print("Value of A: " + str(float(value_A)))
    print("Value of B: " + str(float(value_B)))
    print("Total value: " + str(float(value_total)))
    print("\n")
    
    action_values += [Trade_Model.output_values[-1]]
    
    plt.clf()
    plt.plot([i for i in range(120)], previous_rates[-120:])
    plt.plot([i+(120-len(action_values)) for i in range(len(action_values))], action_values)
    plt.pause(0.001)
    
    if last_balance_A != balance_A:
        last_input_values = prev_input_values
        last_decision = prev_decision
        last_value_total = prev_value_total
        
        start_flag = False
        
    last_balance_A = balance_A
    
    prev_input_values = change_moving_average_rates[-Trade_Model.input_count:].copy()
    prev_decision = (Trade_Model.output_values[-1] >= 0.5)
    prev_value_total = value_total
    
    if not start_flag:
        action = last_decision if value_total >= last_value_total else not last_decision
        
        Trade_Data_train.load(input_values=last_input_values, target_values=[Decimal(1) if action else Decimal(0)], stream=False, shift_count=Trade_Model.input_count)
        Trade_Data_validate.load(input_values=[], target_values=[], stream=False, shift_count=Trade_Model.input_count)
        
        Trade_Model.train(Trade_Data_train, Trade_Data_validate)
        Trade_Model.save()
    
    if len(previous_rates) > 600:
        previous_rates = previous_rates[-600:]
    if len(action_values) > 120:
        action_values = action_values[-120:]
        
    sleep(0.05)