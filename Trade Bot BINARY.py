import matplotlib.pyplot as plt
from DeepLearner import *
from decimal import *
from time import *
import requests

getcontext().prec = 64

model_name = input("Model name: ")

Trade_Model = Model_Class()
Trade_Model.load(model_name, min_diff=0.00000001, learning_rate=0.0001, cycles=5)

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

value_A = Decimal(request_getValue["valueA"])
value_B = Decimal(request_getValue["valueB"])

value_total = value_A + value_B

last_value_total = value_total
last_decision = True
decision = True

start_flag = True

while True:
    request_getBalance = requests.get(url + "/getBalance", json = {"userID" : userID}).json()
    
    balance_A = Decimal(request_getBalance["balanceA"])
    balance_B = Decimal(request_getBalance["balanceB"])
    
    request_getHistoricPrices = requests.get(url + "/getHistoricPrices", json = {"userID" : userID, "onlyRecent" : True}).json()
    previous_rates += [Decimal(i) for i in request_getHistoricPrices["avgPrice"]]
    
    unit_rate = previous_rates[-1]

    moving_average_previous_rates = [sum(previous_rates[i:i+average_size])/Decimal(average_size) for i in range(len(previous_rates)-average_size+1)]
    
    change_moving_average_rates = [moving_average_previous_rates[i+1]/moving_average_previous_rates[i] for i in range(len(moving_average_previous_rates)-1)]
    
    
    
    if start_flag:
        last_input_values = change_moving_average_rates[-Trade_Model.input_count:].copy()
    
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
    
    

    print("Ask: " + str((Trade_Model.output_values[-1] < 0.5)))
    print("Bid: " + str((Trade_Model.output_values[-1] >= 0.5)))
    print("Value of A: " + str(float(value_A)))
    print("Value of B: " + str(float(value_B)))
    print("Total value: " + str(float(value_total)))
    print("\n")
    
    
    
    if last_balance_A != balance_A:
        last_input_values = change_moving_average_rates[-Trade_Model.input_count:]
        last_decision = decision
        
    last_balance_A = balance_A
    decision = last_decision if value_total >= last_value_total else not last_decision
    
    last_value_total = value_total
        
    start_flag = False
    
    Trade_Data_train.load(input_values=last_input_values, target_values=[Decimal(1) if decision else Decimal(0)], stream=False, shift_count=Trade_Model.input_count)
    Trade_Data_validate.load(input_values=[], target_values=[], stream=False, shift_count=Trade_Model.input_count)
    
    Trade_Model.train(Trade_Data_train, Trade_Data_validate)
    Trade_Model.save()
    
    if len(previous_rates) > 600:
        previous_rates = previous_rates[-600:]
        
    sleep(0.05)