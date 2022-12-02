import requests

url = "http://127.0.0.1:8080"

x = requests.get(url+"/register")
print(x.json())

y = requests.post(url+"/placeOrder", json={"userID" : x.json()["userID"],
                   "ask" : True,
                   "unitPrice" : 8.0,
                   "quantity" : 1.0})
print(x.text)
print(y.text)