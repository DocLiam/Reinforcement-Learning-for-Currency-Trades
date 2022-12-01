from flask import Flask, request, jsonify
from datetime import datetime
from decimal import *
from threading import *
from time import *

app = Flask(__name__)

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
        
    def getUserID(self):
        return self.__userID
    
    def getBalanceA(self):
        return self.__balance_A
    
    def getBalanceB(self):
        return self.__balance_B
        
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
        return {
                "Value in A" : self.__balance_A + self.getPrice()["avgBidPrice"]*self.__balance_B, 
                "Value in B" : self.__balance_B + self.getPrice()["avgAskPrice"]*self.__balance_A
            }

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
        print(new_balances)
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
                    
                    self.__bid_quantity -= OrderObject.getQuantity()
                    self.__bid_sum -= OrderObject.getPrice() * OrderObject.getQuantity()
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
                    
                    self.__ask_quantity -= OrderObject.getQuantity()
                    self.__ask_sum -= OrderObject.getPrice() * OrderObject.getQuantity()
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
            (lambda : (self.__ask_sum/self.__ask_quantity + self.__bid_sum/self.__bid_quantity)/2.0)
        )

    def visualiseQueue(self):
        for i in self.__ask_queue:
            print("Asking ", i.getPrice(), " for x", i.getQuantity(), sep = "")
        for i in self.__bid_queue:
            print("Bidding ", i.getPrice(), " for x", i.getQuantity(), sep = "")


@app.get("/register")
def register():
    global current_userID, user_dict
    
    current_userID += 1
    user_dict[current_userID] = User(current_userID, balance_A = 10.0, balance_B = 10.0)
    
    return {
        "success" : True,
        "userID" : current_userID
    }
    
@app.get("/getBalance")
def getPrice():
    if request.is_json:
        request_data = request.get_json()
        userObject = user_dict[request_data["userID"]]
        
        return {
            "success" : True,
            "balanceA" : userObject.getBalanceA(),
            "balanceB" : userObject.getBalanceB()
        }
    
    return {"success" : False}
    
@app.get("/getPrice")
def getPrice2(): #Electric Boogaloo
    avg_price_data = OrderQueueObject.getAvgPrice()
    
    return {
        "success" : True,
        "avgAskPrice" : avg_price_data[0],
        "avgBidPrice" : avg_price_data[1],
        "avgPrice" : avg_price_data[2]
    }

@app.get("/getHistoricPrices")
def getHistoricPrices():
    return {
        "success" : True,
        "avgAskPrice" : historic_ask_prices,
        "avgBidPrice" : historic_bid_prices,
        "avgPrice" : historic_prices
    }
    
@app.post("/placeOrder")
def placeOrder():
    if request.is_json:
        global OrderQueueObject
        
        request_data = request.get_json()
        
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
        
    return {"success": False}

def updatePrices():
    global historic_ask_prices, historic_bid_prices, historic_prices
    
    while True:
        avg_price_data = OrderQueueObject.getAvgPrice()
        
        historic_ask_prices.append(1.0 if OrderQueueObject.askQueueEmpty() else avg_price_data[0]())
        historic_bid_prices.append(1.0 if OrderQueueObject.bidQueueEmpty() else avg_price_data[1]())
        historic_prices.append(1.0 if OrderQueueObject.askQueueEmpty() or OrderQueueObject.bidQueueEmpty() else avg_price_data[2]())
        
        sleep(1)

        print("Ask Price: ", historic_ask_prices[-1])
        print("Bid Price: ", historic_bid_prices[-1])
        print("Price: ", historic_prices[-1])
        
        OrderQueueObject.visualiseQueue()

if __name__ == "__main__":
    current_userID = -1
    user_dict = {}

    OrderQueueObject = OrderQueue()
    
    historic_ask_prices = []
    historic_bid_prices = []
    historic_prices = []
    
    update_prices_thread = Thread(target=updatePrices, name="updatePrices")
    update_prices_thread.start()

    app.run(host="127.0.0.1", port=8080)