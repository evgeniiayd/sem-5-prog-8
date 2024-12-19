import requests

url = "http://127.0.0.1:8000/token"
data = {
    "username": "employee",
    "password": "password"
}

response = requests.post(url, data=data)

print(response.json())

res = response.json()
token = res['access_token']

url = "http://127.0.0.1:8000/bonuses/"
headers = {
    "Authorization": f"Bearer {token}"
}

response = requests.get(url, headers=headers)

print(response.json())