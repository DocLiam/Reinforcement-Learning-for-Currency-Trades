import requests

url = "http://127.0.0.1:8080"



x = requests.get(url+"/register", json={"startBalanceA" : 100.0, "startBalanceB" : 100.0})
print(x.json())

y = requests.post(url+"/placeOrder", json={"userID" : x.json()["userID"],
                   "ask" : True,
                   "unitPrice" : 0.7,
                   "quantity" : 50.0})

print(x.text)
print(y.text)

x = requests.get(url+"/register", json={"startBalanceA" : 100.0, "startBalanceB" : 100.0})
print(x.json())

y = requests.post(url+"/placeOrder", json={"userID" : x.json()["userID"],
                   "ask" : True,
                   "unitPrice" : 1.7,
                   "quantity" : 50.0})

print(x.text)
print(y.text)

x = requests.get(url+"/register", json={"startBalanceA" : 100.0, "startBalanceB" : 100.0})
print(x.json())

y = requests.post(url+"/placeOrder", json={"userID" : x.json()["userID"],
                   "ask" : False,
                   "unitPrice" : 0.4,
                   "quantity" : 50.0})

print(x.text)
print(y.text)

x = requests.get(url+"/register", json={"startBalanceA" : 100.0, "startBalanceB" : 100.0})
print(x.json())

y = requests.post(url+"/placeOrder", json={"userID" : x.json()["userID"],
                   "ask" : False,
                   "unitPrice" : 1.4,
                   "quantity" : 50.0})

print(x.text)
print(y.text)