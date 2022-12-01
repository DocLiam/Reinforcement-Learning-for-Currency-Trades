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
    def __init__(self, userID, balance_A, balance_B):
        self.__userID = userID
        self.__balance_A = balance_A
        self.__balance_B = balance_B
        
    def getUserID(self):
        return self.__userID
    
    def getBalanceA(self):
        return self.__balance_A
    
    def getBalanceB(self):
        return self.__balance_B
        
    def changeBalance(self, ask, unit_price, quantity):
        if ask:
            self.__balance_A -= quantity
            self.__balance_B += unit_price*quantity
        else:
            self.__balance_A += quantity
            self.__balance_B -= unit_price*quantity
    
    def testChangeBalance(self, ask, unit_price, quantity):
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
    def __init__(self, userID, ask, unit_price, quantity):
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
    
    def checkValid(self, user_dict):
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
        
        # find position
        # this will be price dependent, and at the first possible opportunity
        # insert object in there
        # ?
        # profit
        
        if ThisOrderObject.getAsk(): #Ask, so highest price is ideal for seller. 
            index = len(self.__ask_queue)
            for ExistingOrderObject in self.__ask_queue[::-5]+[]: #While orders are better priced for the buyer, move the index left
                if ExistingOrderObject.getPrice() > ThisOrderObject.getPrice(): #triggers once a worse order has been found
                    for i in range(index, len(self.__ask_queue)): #moves to the right
                        if self.__ask_queue[i].getPrice() <= ThisOrderObject.getPrice(): #finds the same or better order
                            index = i
                            continue
                index -= 5
            index = 0

            self.__ask_queue.insert(index, ThisOrderObject)

            # increase the avg tallies appropriately
            self.__ask_sum += ThisOrderObject.getPrice()*ThisOrderObject.getQuantity()
            self.__ask_quantity += ThisOrderObject.getQuantity()
                            
        else:
            index = len(self.__bid_queue)
            for ExistingOrderObject in self.__bid_queue[::-5]+[]: #While orders are better priced for the buyer, move the index left
                if ExistingOrderObject.getPrice() > ThisOrderObject.getPrice(): #triggers once a worse order has been found
                    for i in range(index, len(self.__bid_queue)): #moves to the right
                        if self.__bid_queue[i].getPrice() <= ThisOrderObject.getPrice(): #finds the same or better order
                            index = i
                            continue
                index -= 5
            index = 0

            self.__bid_queue.insert(index, ThisOrderObject)

            # increase the avg tallies appropriately
            self.__bid_sum += ThisOrderObject.getPrice()*ThisOrderObject.getQuantity()
            self.__bid_quantity += ThisOrderObject.getQuantity()

    def removeOrder(self, ask, userID):
        if ask:
            OrderObject = next(filter(lambda x : x.getUserID == userID, self.__ask_queue))
            
            if OrderObject:
                self.__ask_queue.remove(OrderObject)
        else:
            OrderObject = next(filter(lambda x : x.getUserID == userID, self.__bid_queue))
            
            if OrderObject:
                self.__bid_queue.remove(OrderObject)
    
    def fillOrder(self, OrderObject):
        pass

    def getTopPrice(self, OrderObject):
        pass

    def getAvgPrice(self):
        return self.__ask_sum/self.__ask_quantity, self.__bid_sum/self.__bid_quantity, (self.__ask_sum/self.__ask_quantity + self.__bid_sum/self.__bid_quantity)/2.0

    def visualiseQueue(self, ask = True):
        if ask:
            for i in self.__ask_queue:
                print(i.getPrice(), i.getQuantity())
        else:
            for i in self.__bid_queue:
                print(i.getPrice(), i.getQuantity())


@app.get("/register")
def register():
    global current_userID, user_dict
    
    current_userID += 1
    user_dict = {current_userID : User(current_userID, balance_A = 1.0, balance_B = 1.0)}
    
    return {
        "success" : True,
        "userID" : current_userID
    }
    
@app.get("/getbalance")
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
def getPrice():
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
        request_data = request.get_json()
        
        OrderObject = Order(request_data["userID"],
                            request_data["ask"],
                            request_data["unitPrice"],
                            request_data["quantity"])
        
        if not OrderObject.checkValid(user_dict):
            return {"success": False}
        else:
            pass
        
    return {"success": False}

def updatePrices():
    global historic_ask_prices, historic_bid_prices, historic_prices
    
    while True:
        historic_ask_prices.append(1.0 if OrderQueueObject.askQueueEmpty() else OrderQueueObject.getAvgPrice()[0])
        historic_bid_prices.append(1.0 if OrderQueueObject.bidQueueEmpty() else OrderQueueObject.getAvgPrice()[1])
        historic_prices.append(1.0 if OrderQueueObject.askQueueEmpty() or OrderQueueObject.askQueueEmpty() else OrderQueueObject.getAvgPrice()[2])
        
        sleep(1)

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