import requests

url = "http://127.0.0.1:8080"

x = requests.get(url+"/register")
print(x.json())

y = requests.post(url+"/placeOrder", json={"userID" : x.json()["userID"],
                   "ask" : False,
                   "unitPrice" : 2.1,
                   "quantity" : 1.5})
print(x.text)
print(y.text)