from flask import Flask, request, jsonify
from datetime import datetime
from decimal import *

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
        user = user_dict[self.__userID]
        
        newBalances = user.testChangeBalance(self.__ask, self.__unit_price, self.__quantity)
        
        if newBalances[0] < 0 or newBalances[1] < 0:
            return False
        else:
            return True
    

class OrderQueue():
    def __init__(self):
        self.__ask_queue = []
        self.__bid_queue = []
        
        pass

    def createOrder(self, userID, isTypeAsk, unit_price, quantity):
        ThisOrder = Order(userID, isTypeAsk, unit_price, quantity)
        if not ThisOrder.getValid(userID):
            return False
        # find position
        # this will be price dependent, and at the first possible opportunity
        # insert object in there
        # ?
        # profit
        
        if isTypeAsk:
            index = len(self.__ask_queue)
            for Orders in self.__ask_queue[::-5]:
                if Orders.getPrice > ThisOrder.getPrice:
                    for i in range(index, len(ask_order_list)):
                        if self.__ask_queue[i].getPrice <= ThisOrder.getPrice:
                            index = i
                            continue

                index += 5
                            
        else:
            pass

    def fillOrder(self, isTypeAsk, quantity, best_unit_price):
        pass

    def getTopPrice(self, isTypeAsk, quantity):
        pass

    def getAvgPrice(self):
        pass
    

def avgPrice(order_list):
    totalQuantity = 0
    totalWeightedPrice = 0
    
    for order in order_list:
        if order.getAsk():
            totalQuantity += order.getQuantity()
            totalWeightedPrice += order.getPrice()*order.getQuantity()
    
    totalPrice = totalWeightedPrice/totalQuantity
    
    return totalPrice

@app.get("/register")
def register():
    global next_userID, user_dict
    
    current_userID = next_UserID
    
    user_dict = {current_userID : User(current_userID, balance_A = Decimal(1), balance_B = Decimal(1))}
    
    next_userID += 1
    
    return {
        "success": True,
        "userID": current_userID
    }

@app.get("/getPrice")
def getPrice():
    avg_ask_price = avgPrice(ask_order_list)
    avg_bid_price = avgPrice(bid_order_list)
    
    avg_price = avgPrice(ask_order_list+bid_order_list)
    
    return {
        "success": True,
        "avgAskPrice": avg_ask_price,
        "avgBidPrice": avg_bid_price
    }
    
@app.post("/placeOrder")
def placeOrder():
    if request.is_json:
        requestData = request.get_json()
        
        
    return {"success": False}


if __name__ == "__main__":
    next_UserID = 0
    
    user_dict = {}

    ask_order_list = [
        Order(
            userID = 0, 
            ask = True, 
            unit_price = Decimal(1), 
            quantity = Decimal(1000)), 
        Order(
            userID = 1, 
            ask = True, 
            unit_price = Decimal(1.5), 
            quantity = Decimal(500))
        ]
    bid_order_list = []
    print(avgPrice(ask_order_list))

    app.run(host="127.0.0.1", port=8080)