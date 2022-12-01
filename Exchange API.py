from flask import Flask, request, jsonify
from datetime import datetime
from decimal import *
import asyncio

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

        self.__ask_sum = 0
        self.__ask_quantity = 0
        
        pass

    def createOrder(self, userID, is_type_ask, unit_price, quantity):
        ThisOrder = Order(userID, is_type_ask, unit_price, quantity)
        
        # find position
        # this will be price dependent, and at the first possible opportunity
        # insert object in there
        # ?
        # profit
        
        if is_type_ask: #Ask, so highest price is ideal for seller. 
            index = len(self.__ask_queue)
            for OrderObject in self.__ask_queue[::-5]+[]: #While orders are better priced for the buyer, move the index left
                if OrderObject.getPrice() > ThisOrder.getPrice(): #triggers once a worse order has been found
                    for i in range(index, len(self.__ask_queue)): #moves to the right
                        if self.__ask_queue[i].getPrice() <= ThisOrder.getPrice(): #finds the same or better order
                            index = i
                            continue
                index -= 5
            index = 0

            self.__ask_queue.insert(index, ThisOrder)

            # increase the avg tallies appropriately
            self.__ask_sum += unit_price * quantity
            self.__ask_quantity += quantity
                            
        else:
            index = len(self.__bid_queue)
            for OrderObject in self.__bid_queue[::-5]+[]: #While orders are better priced for the buyer, move the index left
                if OrderObject.getPrice() < ThisOrder.getPrice(): #triggers once a worse order has been found
                    for i in range(index, len(self.__bid_queue)): #moves to the right
                        if self.__bid_queue[i].getPrice() >= ThisOrder.getPrice(): #finds the same or better order
                            index = i
                            continue
                index -= 5
            index = 0

            self.__bid_queue.insert(index, ThisOrder)

            # increase the avg tallies appropriately
            self.__bid_sum += unit_price * quantity
            self.__bid_quantity += quantity

    def fillOrder(self, isTypeAsk, quantity, best_unit_price):
        pass

    def getTopPrice(self, isTypeAsk, quantity):
        pass

    def getAvgPrice(self):
        return {
            "avgAskPrice" : self.__ask_sum/self.__ask_quantity,
            "avgBidPrice" : self.__bid_sum/self.__bid_quantity,
            "avgPrice" : (self.__ask_sum/self.__ask_quantity + self.__bid_sum/self.__bid_quantity)//Decimal(2)
        }

    def visualiseQueue(self, ask = True):
        if ask:
            for i in self.__ask_queue:
                print(i.getPrice(), i.getQuantity())
        else:
            for i in self.__bid_queue:
                print(i.getPrice(), i.getQuantity())


@app.get("/register")
def register():
    global next_userID, user_dict
    
    current_userID = next_UserID
    user_dict = {current_userID : User(current_userID, balance_A = Decimal(1), balance_B = Decimal(1))}
    next_userID += 1
    
    return {
        "success" : True,
        "userID" : current_userID
    }

@app.get("/getPrice")
def getPrice():
    avg_price_Data = OrderQueueObject.getAvgPrice()
    
    return {
        "success" : True,
        "avgAskPrice" : avg_ask_price,
        "avgBidPrice" : avg_bid_price,
        "avgPrice" : avg_price
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
        requestData = request.get_json()
        
        
    return {"success": False}

async def updatePrices():
    global historic_ask_prices, historic_bid_prices, historic_prices
    
    while True:
        historic_ask_prices.append(avgPrice)
        await asyncio.sleep(1)

if __name__ == "__main__":
    next_UserID = 0
    user_dict = {}

    OrderQueueObject = OrderQueue
    
    historic_ask_prices = []
    historic_bid_prices = []
    historic_prices = []

    app.run(host="127.0.0.1", port=8080)