from requests.structures import CaseInsensitiveDict
import requests, yaml, logging, sys, json

class HandleLocalServer:
  def __init__(self):
    self.sync_settings = self.read_settings()
   
    self.sync_login = 'sync_service'
    self.sync_password = 'sync_service'
    self.n_values = self.sync_settings['n_values']
    self.headers = CaseInsensitiveDict()
    self.headers["Content-Type"] = "application/json"
    self.login_body = {
      "login": self.sync_login,
      "password": self.sync_password
    }
    self.host = "http://" + self.sync_settings['host']
    self.port = str(self.sync_settings['port'])
    #self.route = self.sync_settings['route']
  
  def read_settings(self) -> object:
    with open('../settings/sync.yaml') as file:
      sync_settings = yaml.load(file, Loader=yaml.FullLoader)
      
    return sync_settings['local_server']
  
  def register(self):
    url = self.host + ":" + self.port + "/api/account/register/"
    try:
      req = requests.post(url, params=self.login_body)
      if req.status_code == 200:
        self.login()
        
    except:
      return
    
  def login(self):
    url = self.host + ":" + self.port + "/api/account/login/"
    try:
      req = requests.post(url, params=self.login_body)
      if req.status_code == 200:
          self.headers["Authorization"] = f"Bearer {req.json()['access_token']}"
          return True
          
      self.register()
      
    except:
      return False 
    
  def logout(self):
    url = self.host + ":" + self.port + "/api/account/logout/"
    try:
      req = requests.get(url=url, headers=self.headers)
      if req.status_code == 200:
        return True
    except:
      return False
    
  def get_data(self):
    url = self.host + ":" + self.port + "/api/dut/?limit=" + str(self.n_values)
    try:
      req = requests.get(url=url)
      #req = requests.get(url=url, headers=self.headers)
      if req.status_code != 200:
        return False
      
      return req.json()
    
    except:
      return False
    
  
  def erase_local_data(self, id_array):
    params = {
      "ids": id_array
    }
    
    url = self.host + ":" + self.port + "/api/dut/"
    try:
      req = requests.delete(url=url, headers=self.headers, json=params)
      if req.status_code == 200:
        return True
      return False
    except:
      return False


class HandleServer:
  def __init__(self):
    self.sync_settings = self.read_settings()
    self.sync_login = self.sync_settings['login']
    self.sync_password = self.sync_settings['password']
    self.headers = CaseInsensitiveDict()
    self.headers["Content-Type"] = "application/json"
    self.login_body = {
      "username": self.sync_login,
      "password": self.sync_password
    }
    self.host = "http://" + self.sync_settings['host']
    self.port = str(self.sync_settings['port'])
  
  def read_settings(self) -> object:
    with open('../settings/sync.yaml') as file:
      sync_settings = yaml.load(file, Loader=yaml.FullLoader)
      
    return sync_settings['server']

        
  
  def login(self):
    url = self.host + ":" + self.port + "/api/account/token/"
    try:
      req = requests.post(url, json=self.login_body)
      if req.status_code == 200:
          self.headers["Authorization"] = f"Bearer {req.json()['token']}"
          return True
      
      self.register(self)
      
    except:
      return False
  
  def register(self):
    url = self.host + ":" + self.port + "/api/account/register/"
    requests.post(url, params=self.login_body)
    self.login()
  
  def logout(self):
    url = self.host + ":" + self.port + "/api/account/logout/"
    try:
      req = requests.get(url=url, headers=self.headers)
      if req.status_code == 200:
        return True
      return False
    except:
      return False
  
  def post_data(self, data):
    url = self.host + ":" + self.port + "/api/controlbox/report/sync/"

    try:
      req = requests.post(url=url, json=data, headers=self.headers)   
      if (req.status_code == 200):
        return True
      return False
    except:
      return False

if __name__ == '__main__':
  
  logging.basicConfig(
      level=logging.DEBUG,
      format='%(asctime)s %(name)s %(levelname)s %(message)s',
      filename='sync.log',
      filemode='a'
  )
  
  logger = logging.getLogger(__name__)
  logger.debug("Sync service started")
  
  local_sync = HandleLocalServer()
  server_sync = HandleServer()
  
  # if(not local_sync.login()):
  #   logger.error("Was not possible to execute local login")
  #   sys.exit()
 
  if(not server_sync.login()): 
    logger.error("Was not possible to execute server login")
    sys.exit()
  
  while True:
    data = local_sync.get_data()
    if not data:
      logger.debug("Any data was returned from local database")
      break
   
    if (server_sync.post_data(data)):
      logger.debug("Data posted")
    else:
       logger.error("Was not possible to post data")
       break
    
    id_array = list(map(lambda value: value['id'], data))
    print(id_array)
   
    if (local_sync.erase_local_data(id_array)):
      logger.debug("Data deleted")
    else:
      logger.error("Was not possible erase data from local database")
      break
  
  # if not local_sync.logout():
  #   logger.error("Was not possible execute logout from local server")
  # if not server_sync.logout():
  #   logger.error("Was not possible execute logout from server")
    
      
    
  
  
  
  