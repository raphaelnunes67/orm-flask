import json, requests
from requests.structures import CaseInsensitiveDict

class ApiRequests(object):

    def __init__(self, settings):
        self.settings = settings
        self.route_base = 'http://{host}:{port}/api'.format(
          host=str(self.settings['api']['host']),
          port=str(self.settings['api']['port'])
        )
        self.body = {
          "login" : self.settings['api']['login'],
          "password": self.settings['api']['password']
        } 
        self.headers = CaseInsensitiveDict()
        self.headers["Content-Type"] = "application/json"
        
    def send_dut_info(self, dut):
        
        self.login()
        result = self.post(dut)
        self.logout()
    
        return result
      
      
    def login(self):
        url = self.route_base + '/login'
      
        req = requests.post(url, params=self.body)
      
        if req.status_code == 200:
            self.headers["Authorization"] = f"Bearer {req.json()['access_token']}"
            return
      
        self.register()
      
    
    def register(self):
            url = self.route_base + '/register'
            req = requests.post(url, params=self.body)
            self.login()
      
    
    def logout(self):
            url = self.route_base + '/logout'
            req = requests.get(url=url, headers=self.headers)

    def post(self, dut):
            url = self.route_base + '/sysinfos'
            data = json.loads(dut.toJSON())
            req = requests.post(url, headers=self.headers, json=data)
            
            return True if req.status_code == 201 or req.status_code == 200 else False