from datetime import datetime
from decimal import *
from threading import *
from time import *
import matplotlib.pyplot as plt
from random import *
from DeepLearner import *

getcontext().prec = 64

fig = plt.figure(figsize = (10, 5))

# variables : separate tokens by underscore
# functions : first token is lowercase, every other token starts with capital

# ask : Buy B with A (like asking USD for BTC)
# bid : Buy A with B (vice versa)
# order : an object that has a certain amount of A or B and wants a certain rate.
# price : Always in B per A
# quantity : Always in amount of A?

class User:
    def __init__(self, userID:int, balance_A:float, balance_B:float):
        self.__userID = userID
        self.__balance_A = balance_A
        self.__balance_B = balance_B
        
        self.__initial_balance_A = balance_A
        self.__initial_balance_B = balance_B
        
        self.value_change_values = []
        
    def getUserID(self):
        return self.__userID
    
    def getBalanceA(self):
        return self.__balance_A
    
    def getBalanceB(self):
        return self.__balance_B

    def getInitialBalanceA(self):
        return self.__initial_balance_A
    
    def getInitialBalanceB(self):
        return self.__initial_balance_B
        
    def changeBalance(self, ask:bool, unit_price:float, quantity:int):
        if ask:
            self.__balance_A -= quantity
            self.__balance_B += unit_price*quantity
        else:
            self.__balance_A += quantity
            self.__balance_B -= unit_price*quantity
    
    def testChangeBalance(self, ask:bool, unit_price:float, quantity:int):
        if ask:
            return self.__balance_A-quantity, self.__balance_B+unit_price*quantity
        else:
            return self.__balance_A+quantity, self.__balance_B-unit_price*quantity

    def getValue(self):
        return self.__balance_A*last_ask_price, self.__balance_B
    
    def getInitialValue(self):
        return self.__initial_balance_A*last_ask_price, self.__initial_balance_B

class Order:
    def __init__(self, userID:int, ask:bool, unit_price:float, quantity:int):
        self.__userID = userID
        self.__ask = ask
        self.__quantity = quantity
        self.__unit_price = unit_price
        self.__order_price = unit_price * quantity
        
        self.__time_stamp = datetime.now()
    
    def getUserID(self):
        return self.__userID
    
    def getAsk(self):
        return self.__ask
    
    def getPrice(self):
        return self.__unit_price
    
    def getQuantity(self):
        return self.__quantity

    def subtractOrder(self, quantity:int):
        self.__quantity -= quantity
    
    def checkValid(self):
        UserObject = user_dict[self.__userID]
        
        new_balances = UserObject.testChangeBalance(self.__ask, self.__unit_price, self.__quantity)
        
        if new_balances[0] < 0 or new_balances[1] < 0:
            return False
        else:
            return True
    
class OrderQueue():
    def __init__(self):
        self.__ask_queue = []
        self.__bid_queue = []

        self.__ask_sum = 0
        self.__ask_quantity = 0

        self.__bid_sum = 0
        self.__bid_quantity = 0

    def askQueueEmpty(self):
        return len(self.__ask_queue) == 0
    
    def bidQueueEmpty(self):
        return len(self.__bid_queue) == 0
    
    def insertOrder(self, ThisOrderObject):
        flag = False
        # find position
        # this will be price dependent, and at the first possible opportunity
        # insert object in there
        # ?
        # profit
        
        if ThisOrderObject.getAsk(): #Ask, so highest price is ideal for seller. 
            index = 0

            for ExistingOrderObject in self.__ask_queue: #While orders are better priced for the buyer, move the index left
                if ExistingOrderObject.getPrice() > ThisOrderObject.getPrice(): #triggers once a worse order has been found
                    break
                else:
                    index += 1

            self.__ask_queue.insert(index, ThisOrderObject)

            # increase the avg tallies appropriately
            self.__ask_sum += ThisOrderObject.getPrice()*ThisOrderObject.getQuantity()
            self.__ask_quantity += ThisOrderObject.getQuantity()
                            
        else:
            index = 0

            for ExistingOrderObject in self.__bid_queue: #While orders are better priced for the buyer, move the index left
                if ExistingOrderObject.getPrice() < ThisOrderObject.getPrice(): #triggers once a worse order has been found
                    break
                else:
                    index += 1

            self.__bid_queue.insert(index, ThisOrderObject)

            # increase the avg tallies appropriately
            self.__bid_sum += ThisOrderObject.getPrice()*ThisOrderObject.getQuantity()
            self.__bid_quantity += ThisOrderObject.getQuantity()

    def removeOrder(self, ask, userID):
        if ask:
            for OrderObject in self.__ask_queue:
                if OrderObject.getUserID() == userID:
                    self.__ask_sum -= OrderObject.getPrice() * OrderObject.getQuantity()
                    self.__ask_quantity -= OrderObject.getQuantity()
                    self.__ask_queue.remove(OrderObject)
                    break
        else:
            for OrderObject in self.__bid_queue:
                if OrderObject.getUserID() == userID:
                    self.__bid_sum -= OrderObject.getPrice() * OrderObject.getQuantity()
                    self.__bid_quantity -= OrderObject.getQuantity()
                    self.__bid_queue.remove(OrderObject)
                    break
    
    def fillOrder(self, TempOrder:Order):
        temp_userID = TempOrder.getUserID()
        TempUser:User = user_dict[temp_userID]
        

        if TempOrder.getAsk():
            while len(self.__bid_queue) > 0:
                OrderObject = self.__bid_queue[0]
                
                if TempOrder.getPrice() > OrderObject.getPrice():
                    break
                
                order_userID = OrderObject.getUserID()
                OrderUser = user_dict[order_userID]
                
                if TempOrder.getQuantity() >= OrderObject.getQuantity():
                    change_quantity = OrderObject.getQuantity()
                    unit_price = OrderObject.getPrice()
                    
                    TempUser.changeBalance(TempOrder.getAsk(), unit_price, change_quantity)
                    OrderUser.changeBalance(OrderObject.getAsk(), unit_price, change_quantity)

                    TempOrder.subtractOrder(change_quantity)
                    OrderObject.subtractOrder(change_quantity)
                    
                    self.removeOrder(not TempOrder.getAsk(), order_userID)
                else:
                    change_quantity = TempOrder.getQuantity()
                    unit_price = OrderObject.getPrice()
                    
                    TempUser.changeBalance(TempOrder.getAsk(), unit_price, change_quantity)
                    OrderUser.changeBalance(OrderObject.getAsk(), unit_price, change_quantity)

                    TempOrder.subtractOrder(change_quantity)
                    OrderObject.subtractOrder(change_quantity)
                    
                    self.__bid_quantity -= change_quantity
                    self.__bid_sum -= unit_price * change_quantity
                    break
            
            if TempOrder.getQuantity() > 0:
                self.insertOrder(TempOrder)
            #Recreate order and add it to the appropriate location.
            #Avoid execution by returning the function.
        else:
            while len(self.__ask_queue) > 0:
                OrderObject = self.__ask_queue[0]
                
                if TempOrder.getPrice() < OrderObject.getPrice():
                    break
                
                order_userID = OrderObject.getUserID()
                OrderUser = user_dict[order_userID]
                
                if TempOrder.getQuantity() >= OrderObject.getQuantity():
                    change_quantity = OrderObject.getQuantity()
                    unit_price = OrderObject.getPrice()
                    
                    TempUser.changeBalance(TempOrder.getAsk(), unit_price, change_quantity)
                    OrderUser.changeBalance(OrderObject.getAsk(), unit_price, change_quantity)

                    TempOrder.subtractOrder(change_quantity)
                    OrderObject.subtractOrder(change_quantity)
                    
                    self.removeOrder(not TempOrder.getAsk(), order_userID)
                else:
                    change_quantity = TempOrder.getQuantity()
                    unit_price = OrderObject.getPrice()
                    
                    TempUser.changeBalance(TempOrder.getAsk(), unit_price, change_quantity)
                    OrderUser.changeBalance(OrderObject.getAsk(), unit_price, change_quantity)

                    TempOrder.subtractOrder(change_quantity)
                    OrderObject.subtractOrder(change_quantity)
                    
                    self.__ask_quantity -= change_quantity
                    self.__ask_sum -= unit_price * change_quantity
                    break
            
            if TempOrder.getQuantity() > 0:
                self.insertOrder(TempOrder)
            #Recreate order and add it to the appropriate location.
            #Avoid execution by returning the function.

    def getTopPrice(self, amount):
        pass

    def getAvgPrice(self):
        return (
            (lambda : self.__ask_sum/self.__ask_quantity), 
            (lambda : self.__bid_sum/self.__bid_quantity), 
            (lambda : ((self.__ask_sum/self.__ask_quantity) + (self.__bid_sum/self.__bid_quantity))/2.0)
        )

    def visualiseQueue(self):
        for i in self.__ask_queue:
            print("Asking ", i.getPrice(), " for x", i.getQuantity(), sep = "")
        for i in self.__bid_queue:
            print("Bidding ", i.getPrice(), " for x", i.getQuantity(), sep = "")

def register(request_data):
    global current_userID, user_dict
    
    current_userID += 1
    user_dict[current_userID] = User(current_userID, balance_A = request_data["startBalanceA"], balance_B = request_data["startBalanceB"])
    
    return {
        "success" : True,
        "userID" : current_userID
    }
    
def getBalance(request_data):
    userObject = user_dict[request_data["userID"]]
    
    return {
        "success" : True,
        "balanceA" : userObject.getBalanceA(),
        "balanceB" : userObject.getBalanceB()
    }

def getValue(request_data):
    userObject = user_dict[request_data["userID"]]
    
    user_value = userObject.getValue()
    
    return {
        "success" : True,
        "valueA" : user_value[0],
        "valueB" : user_value[1]
    }
    
def getCurrentPrice():
    return {
        "success" : True,
        "avgAskPrice" : last_ask_price,
        "avgBidPrice" : last_bid_price,
        "avgPrice" : last_price
    }

def getHistoricPrices(request_data):
    global time_dict, time_passed
    
    index = 0
    
    if request_data["onlyRecent"]:
        index = time_dict[request_data["userID"]] - time_passed
    
    time_dict[request_data["userID"]] = time_passed
    
    return {
        "success" : True,
        "avgAskPrice" : historic_ask_prices[index:],
        "avgBidPrice" : historic_bid_prices[index:],
        "avgPrice" : historic_prices[index:]
    }
    
def placeOrder(request_data):
    global OrderQueueObject
    
    OrderObject = Order(request_data["userID"],
                        request_data["ask"],
                        request_data["unitPrice"],
                        request_data["quantity"])
    
    if not OrderObject.checkValid():
        return {"success": False}
    else:
        OrderQueueObject.removeOrder(OrderObject.getAsk(), OrderObject.getUserID())
        
        OrderQueueObject.fillOrder(OrderObject)
        
        return {"success" : True}

def updatePrices():
    global historic_ask_prices, historic_bid_prices, historic_prices, time_passed, time_values, value_values
    global last_ask_price, last_bid_price, last_price
    
    while True:
        avg_price_data = OrderQueueObject.getAvgPrice()
        
        historic_ask_prices.append(last_ask_price if OrderQueueObject.askQueueEmpty() else avg_price_data[0]())
        historic_bid_prices.append(last_bid_price if OrderQueueObject.bidQueueEmpty() else avg_price_data[1]())
        historic_prices.append(last_price if OrderQueueObject.askQueueEmpty() or OrderQueueObject.bidQueueEmpty() else avg_price_data[2]())
        
        last_ask_price = historic_ask_prices[-1]
        last_bid_price = historic_bid_prices[-1]
        last_price = historic_prices[-1]
        
        sleep(0.2)

        print("Ask Price: ", historic_ask_prices[-1])
        print("Bid Price: ", historic_bid_prices[-1])
        print("Price: ", historic_prices[-1])
        
        OrderQueueObject.visualiseQueue()
        
        time_values.append(time_passed)
        
        time_passed += 1
        
        avg_value = 0
        
        for userID in user_dict:
            UserObject = user_dict[userID]
            user_value = UserObject.getValue()
            user_initial_value = UserObject.getInitialValue()
            
            UserObject.value_change_values.append((user_value[0]+user_value[1])/(user_initial_value[0]+user_initial_value[1]))
            
            avg_value += (user_value[0]+user_value[1])/len(user_dict)
            
        value_values.append(avg_value)
        
        print("AVERAGE VALUE: ", avg_value)
        
        if len(time_values) > 200:
            time_values = time_values[-200:]
        if len(value_values) > 200:
            value_values = value_values[-200:]
        if len(historic_ask_prices) > 600:
            historic_ask_prices = historic_ask_prices[-600:]
        if len(historic_bid_prices) > 600:
            historic_bid_prices = historic_bid_prices[-600:]
        if len(historic_prices) > 600:
            historic_prices = historic_prices[-600:]

def visualiseValue():
    while True:
        plt.clf()
        plt.plot(time_values[-60:], historic_prices[-60:])
        for userID in user_dict:
            UserObject = user_dict[userID]
            
            color = "red" if userID < 8 else "green"
            
            plt.plot(time_values[-min(60, len(UserObject.value_change_values)):], UserObject.value_change_values, color=color)
        plt.pause(0.001)

def botRatio(model_name):
    Trade_Model = Model_Class()
    Trade_Model.load(model_name, min_diff=0.00000001, learning_rate=0.00002, cycles=5)

    Trade_Data_test = Data_Class()

    Trade_Data_train = Data_Class()
    Trade_Data_validate = Data_Class()

    Trade_Data_uncertainty = Data_Class()


    request_register = register({"startBalanceA" : 100.0, "startBalanceB" : 100.0})

    userID = request_register["userID"]

    predicted_count = 8

    average_size = 5



    x_values = [i for i in range(Trade_Model.input_count+predicted_count)]

    request_getHistoricPrices = getHistoricPrices({"userID" : userID, "onlyRecent" : False})
    previous_rates = [Decimal(i) for i in request_getHistoricPrices["avgPrice"]]

    while True:
        request_getBalance = getBalance({"userID" : userID})
        
        balance_A = Decimal(request_getBalance["balanceA"])
        balance_B = Decimal(request_getBalance["balanceB"])
        
        request_getHistoricPrices = getHistoricPrices({"userID" : userID, "onlyRecent" : True})
        previous_rates += [Decimal(i) for i in request_getHistoricPrices["avgPrice"]]
        
        unit_rate = previous_rates[-1]

        moving_average_previous_rates = [sum(previous_rates[i:i+average_size])/Decimal(average_size) for i in range(len(previous_rates)-average_size+1)]
        
        change_moving_average_rates = [moving_average_previous_rates[i+1]/moving_average_previous_rates[i] for i in range(len(moving_average_previous_rates)-1)]
        
        
        
        Trade_Data_test.load(input_values=change_moving_average_rates[-Trade_Model.input_count:], target_values=[], stream=False, shift_count=Trade_Model.input_count)
        
        Trade_Model.recursive_test(Trade_Data_test, loop_count=predicted_count, feedback_count=5, pivot_value=1, auto_adjust=False)



        compounded_multiplier = Decimal(1)
        compounded_moving_change = []
        
        for multiplier in Trade_Model.recursive_output_values:
            compounded_multiplier *= multiplier

            compounded_moving_change.append(compounded_multiplier-Decimal(1))
            
        compounded_actual_change = []

        for change in compounded_moving_change:
            compounded_actual_change.append((moving_average_previous_rates[-1]*(change+Decimal(1)))/unit_rate-Decimal(1))


        step = 10

        uncertainty_values_lower = [Decimal(0) for i in range(predicted_count)]
        uncertainty_values_upper = [Decimal(0) for i in range(predicted_count)]
        
        for h in range(0, len(change_moving_average_rates)-Trade_Model.input_count+1-predicted_count, step):
            Trade_Data_uncertainty.load(input_values=change_moving_average_rates[h:h+Trade_Model.input_count], target_values=[], stream=False, shift_count=Trade_Model.input_count)
            
            Trade_Model.recursive_test(Trade_Data_uncertainty, loop_count=predicted_count, feedback_count=1, pivot_value=1, auto_adjust=False)
            
            
            
            compounded_multiplier_real = Decimal(1)
            compounded_multiplier_uncertainty = Decimal(1)
            
            for i in range(predicted_count):
                compounded_multiplier_real *= change_moving_average_rates[h+Trade_Model.input_count+i]
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
            
        
        
        request_getValue = getValue({"userID" : userID})
        
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
        
        request_placeOrder = placeOrder(order_data)
        
        
        input_values_train = change_moving_average_rates[int(len(change_moving_average_rates)/2)+Trade_Model.input_count:]
        input_values_validate = change_moving_average_rates[:int(len(change_moving_average_rates)/2)]
        
        Trade_Data_train.load(input_values=input_values_train, target_values=[], stream=True, shift_count=1)
        Trade_Data_validate.load(input_values=input_values_validate, target_values=[], stream=True, shift_count=1)
        
        Trade_Model.train(Trade_Data_train, Trade_Data_validate)
        Trade_Model.save()
        
        if len(previous_rates) > 600:
            previous_rates = previous_rates[-600:]

def botBinary(model_name):
    Trade_Model = Model_Class()
    Trade_Model.load(model_name, min_diff=0.00000001, learning_rate=0.0002, cycles=5)

    Trade_Data_test = Data_Class()

    Trade_Data_train = Data_Class()
    Trade_Data_validate = Data_Class()


    request_register = register({"startBalanceA" : 100.0, "startBalanceB" : 100.0})

    userID = request_register["userID"]

    average_size = 6



    request_getHistoricPrices = getHistoricPrices({"userID" : userID, "onlyRecent" : False})
    previous_rates = [Decimal(i) for i in request_getHistoricPrices["avgPrice"]]



    request_getBalance = getBalance({"userID" : userID})

    last_balance_A = Decimal(request_getBalance["balanceA"])

    request_getValue = getValue({"userID" : userID})

    start_flag = True

    last_input_values = []
    last_target_values = []

    action_values = []

    while True:
        request_getBalance = getBalance({"userID" : userID})
        
        balance_A = Decimal(request_getBalance["balanceA"])
        balance_B = Decimal(request_getBalance["balanceB"])
        
        request_getHistoricPrices = getHistoricPrices({"userID" : userID, "onlyRecent" : True})
        previous_rates += [Decimal(i) for i in request_getHistoricPrices["avgPrice"]]
        
        unit_rate = previous_rates[-1]

        moving_average_previous_rates = [sum(previous_rates[i:i+average_size])/Decimal(average_size) for i in range(len(previous_rates)-average_size+1)]
        
        change_moving_average_rates = [moving_average_previous_rates[i+1]/moving_average_previous_rates[i] for i in range(len(moving_average_previous_rates)-1)]
        
        
        
        
        Trade_Data_test.load(input_values=change_moving_average_rates[-Trade_Model.input_count:], target_values=[], stream=False, shift_count=Trade_Model.input_count)
        
        Trade_Model.test(Trade_Data_test)


        
        request_getValue = getValue({"userID" : userID})
        
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
        
        request_placeOrder = placeOrder(order_data)
        
        

        print("Action: " + str(Trade_Model.output_values[-1]))
        print("Value of A: " + str(float(value_A)))
        print("Value of B: " + str(float(value_B)))
        print("Total value: " + str(float(value_total)))
        print("\n")
        
        action_values += [Trade_Model.output_values[-1]]
        
        if last_balance_A != balance_A:
            last_input_values += prev_input_values
            
            if not start_flag:
                action = last_decision if prev_value_total >= last_value_total else not last_decision
                last_target_values += [Decimal(1) if action else Decimal(0)]
            
            last_decision = prev_decision
            last_value_total = prev_value_total
            
            start_flag = False
            
        last_balance_A = balance_A
        
        prev_input_values = change_moving_average_rates[-Trade_Model.input_count:].copy()
        prev_decision = (Trade_Model.output_values[-1] >= 0.5)
        prev_value_total = value_total
        
        if not start_flag:
            action = last_decision if value_total >= last_value_total else not last_decision
            
            temp_last_target_values = last_target_values + [Decimal(1) if action else Decimal(0)]
            
            halfway_index = len(temp_last_target_values)//2
            
            Trade_Data_train.load(input_values=last_input_values[halfway_index*Trade_Model.input_count:], target_values=temp_last_target_values[halfway_index:], stream=False, shift_count=Trade_Model.input_count)
            Trade_Data_validate.load(input_values=last_input_values[:halfway_index*Trade_Model.input_count], target_values=temp_last_target_values[:halfway_index], stream=False, shift_count=Trade_Model.input_count)
            
            Trade_Model.train(Trade_Data_train, Trade_Data_validate)
            Trade_Model.save()
        
        if len(previous_rates) > 600:
            previous_rates = previous_rates[-600:]
        if len(action_values) > 120:
            action_values = action_values[-120:]
        
        sleep(0.1)
        

if __name__ == "__main__":
    current_userID = -1
    user_dict = {}
    
    time_passed = 600
    time_dict = {}

    OrderQueueObject = OrderQueue()
    
    last_ask_price = 1.0
    last_bid_price = 1.0
    last_price = 1.0
    
    historic_ask_prices = [1.0+random() for i in range(time_passed)]
    historic_bid_prices = [1.0+random() for i in range(time_passed)]
    historic_prices = [(historic_ask_prices[i]+historic_bid_prices[i])/2.0 for i in range(time_passed)]
    
    time_values = [i for i in range(time_passed)]
    value_values = [0 for i in range(time_passed)]

    update_prices_thread = Thread(target=updatePrices, name="updatePrices")
    update_prices_thread.start()
    
    fake_user1 = register({"startBalanceA" : 1000.0, "startBalanceB" : 1000.0})
    
    placeOrder({"userID" : fake_user1["userID"],
                   "ask" : True,
                   "unitPrice" : 1.5,
                   "quantity" : 500.0})
    
    fake_user2 = register({"startBalanceA" : 1000.0, "startBalanceB" : 1000.0})
    
    placeOrder({"userID" : fake_user2["userID"],
                   "ask" : True,
                   "unitPrice" : 1.1,
                   "quantity" : 500.0})
    
    fake_user3 = register({"startBalanceA" : 1000.0, "startBalanceB" : 1000.0})
    
    placeOrder({"userID" : fake_user3["userID"],
                   "ask" : False,
                   "unitPrice" : 0.25,
                   "quantity" : 500.0})
    
    fake_user4 = register({"startBalanceA" : 1000.0, "startBalanceB" : 1000.0})
    
    placeOrder({"userID" : fake_user4["userID"],
                   "ask" : False,
                   "unitPrice" : 0.1,
                   "quantity" : 500.0})

    sleep(2)

    model_name_ratio = "BOTRATIO"
    
    for i in range(4):
        bot_ratio_thread = Thread(target=botRatio, name="botRatio", args=(model_name_ratio+str(i+1),))
        bot_ratio_thread.start()
        sleep(0.5)
        
    model_name_binary = "BOTBINARY"
    
    for i in range(6):
        bot_binary_thread = Thread(target=botBinary, name="botBinary", args=(model_name_binary+str(i+1),))
        bot_binary_thread.start()
        sleep(0.5)
    
    visualiseValue()