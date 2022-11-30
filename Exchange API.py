from flask import Flask, request, jsonify
from datetime import datetime
from decimal import *

app = Flask(__name__)

# ask : Buy B with A
# bid : Buy A with B

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

# price : Always in B per A
# quantity : Always in amount of A

class Order:
    def __init__(self, user, ask, price, quantity):
        self.__user = user
        self.__ask = ask
        self.__price = price
        self.__quantity = quantity
        
        self.__time_stamp = datetime.now()
    
    def ask(self):
        return self.__ask
    
    def price(self):
        return self.__price
    
    def quantity(self):
        return self.__quantity
    

order_list = [Order(user = User(ask = True, balance_A = 1000, balance_B = 0), ask = True, price = Decimal(1), quantity = Decimal(1000))]

def avgPrice(order_list):
    askTotalQuantity = 0
    bidTotalQuantity = 0
    
    askTotalWeightedPrice = 0
    bidTotalWeightedPrice = 0
    
    for order in order_list:
        if order.ask():
            askTotalQuantity += order.quantity()
            askTotalWeightedPrice += order.price()*order.quantity()

@app.get("/getPrice")
def getPrice():
    avg_price = avgPrice(order_list)
    
    return {"success": True, "avgAskPrice": avg_price[0], "avgBidPrice": avg_price[1]} 
    
@app.post("/placeOrder")
def placeOrder():
    if request.is_json:
        requestData = request.get_json()
        
    return {"success": False, }

app.run(host="127.0.0.1", port=8080)