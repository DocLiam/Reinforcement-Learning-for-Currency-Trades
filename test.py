import requests

url = "http://127.0.0.1:8080"

x = requests.get(url+"/register", json={"startBalanceA" : 100.0, "startBalanceB" : 100.0})
print(x.json())

y = requests.post(url+"/placeOrder", json={"userID" : x.json()["userID"],
                   "ask" : True,
                   "unitPrice" : 0.2,
                   "quantity" : 50.0})
print(x.text)
print(y.text)