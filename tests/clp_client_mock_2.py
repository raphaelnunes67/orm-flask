import requests
from requests.structures import CaseInsensitiveDict
from time import sleep
from datetime import datetime
import json
from random import randint

def read_register_json():
  with open ('register.json', 'r') as json_file:
    register_json = json.load(json_file)
  return register_json


def save_JWT_token(data):
  with open ('register.json', 'r') as json_file:
    register_json = json.load(json_file)
  
  register_json['JWT_token'] = data['access_token']
  
  with open ('register.json', 'w') as json_file:
    json.dump(register_json, json_file, indent=4) 
  

def register(route_base):
  register_json = read_register_json()
  body = {
    'login':register_json['login'],
    'password': register_json['password']
  }
  req = requests.post(url=route_base+'/register', params=body)
  print (req)

def login(route_base):
  register_json = read_register_json()
  body = {
    'login':register_json['login'],
    'password': register_json['password']
  }
  req = requests.post(url=route_base+'/login', params=body)
  return req

if __name__ == "__main__":
  
  model_base = 'XYZ-ABC'
  route_base = "http://127.0.0.1:5000"
  
  req = login(route_base)
  
  if (req.status_code == 401):
    print("Login failed... Need be a register...")
    register(route_base)
    print("Registered.")
    req = login(route_base)
    
  save_JWT_token (req.json())
  print('JWT token saved')
  
  headers = CaseInsensitiveDict()
  headers["Accept"] = "application/json"
  headers["Authorization"] = f"Bearer {req.json()['access_token']}"
  headers["Content-Type"] = "application/json"
  print(headers)
  while True:
    
    params = { 
      "model": model_base +  str(randint(0,99)).zfill(3),
      "quantity": randint(100, 100000),
      "work_order": "DAMPER"+str(randint(0,9999)).zfill(4)+"-TEST",
      "created_at": datetime.now().isoformat(),
      "details": "Some text for test"
    }
    req = requests.post(url='http://127.0.0.1:5000/sysinfos', headers=headers, json=params)
    print(params)
    print(f'HTTP response code: {req.status_code}')
    if (req.status_code == 401):
      req = login(route_base)
      headers["Authorization"] = f"Bearer {req.json()['access_token']}"
      save_JWT_token (req.json())
    sleep(randint(2, 10))
