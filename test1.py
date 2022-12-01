import requests

url = "http://127.0.0.1:8080"

x = requests.get(url+"/getBalance", json={"userID" : 0})
print(x.json())
