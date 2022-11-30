from flask import Flask, request, jsonify
from datetime import datetime
from decimal import *

app = Flask(__name__)

# variables : separate tokens by underscore
# functions : first token is lowercase, every other token starts with capital

# ask : Buy B with A (like asking USD for BTC)
# bid : Buy A with B (vice versa)
# order : an object that has a certain amount of A or B and wants a certain rate. `buy` divided by `with`

# Slay queen frfr ong you got this danre
# No Thank You
# Why not
# Just coz

class User:
    def __init__(self, balance_A, balance_B):
        self.__balance_A = balance_A
        self.__balance_B = balance_B
        
    def changeBalance(self, ask, price, quantity):
        if ask:
            self.__balance_A -= quantity
            self.__balance_B += price*quantity
        else:
            self.__balance_A += quantity
            self.__balance_B -= price*quantity

    def getValue(self):
        return {
                "Value in A" : self.__balance_A + self.getPrice()["avgBidPrice"]*self.__balance_B, 
                "Value in B" : self.__balance_B + self.getPrice()["avgAskPrice"]*self.__balance_A
            }

# price : Always in B per A
# quantity : Always in amount of A

class Order:
    def __init__(self, user, ask, unit_price, quantity):
        self.__user = user
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
    

class OrderQueue():
    def __init__():
        pass


ask_order_list = [Order(user = User(balance_A = 1000, balance_B = 0), ask = True, unit_price = Decimal(1), quantity = Decimal(1000))]
bid_order_list = []

def avgPrice(order_list):
    totalQuantity = 0
    totalWeightedPrice = 0
    
    for order in order_list:
        if order.getAsk():
            totalQuantity += order.getQuantity()
            totalWeightedPrice += order.getPrice()*order.getQuantity()
    
    totalPrice = totalWeightedPrice/totalQuantity
    
    return totalPrice

def getPriceofSome(order_list, num_units, ask=False):
    pass #TODO
    

@app.get("/getPrice")
def getPrice():
    avg_ask_price = avgPrice(ask_order_list)
    avg_bid_price = avgPrice(bid_order_list)
    
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

print(avgPrice(ask_order_list))

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080)