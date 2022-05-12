def configure_log():
  """
  Configure the log data output.
  """
    
  logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(name)s %(levelname)s %(message)s',
    filename='plc_client.log',
    filemode='w'
  )

def read_route_base():
  """
  Read route base to publish data.
  
  :return: Route base path.
  :rtype: String
  """
  
  with open('plc_client_settings.json', 'r') as json_file:
    route_base = json.load(json_file)['route_base']
      
  return route_base

class PlcMonitor:
  """
  This is a class to perform a data insert client. This class is responsible to
  execute operations like, login, post e logout.

  """
  
  def __init__(self):
    
    self.route_base = read_route_base()
    self.plc_login = 'damper_plc'
    self.plc_password = 'damper_2022'
    self.headers = CaseInsensitiveDict()
    self.headers["Content-Type"] = "application/json"
    self.body = {
      "login": self.plc_login,
      "password": self.plc_password
    }
    
    self.log = logging.getLogger(__name__)
    self.log.debug("PLC Client started")
    
  def register(self):
    req = requests.post(
      url = self.route_base + '/register',
      params= self.body
    )
    
    self.login()
  
  
  def login(self):
    req = requests.post(
      url = self.route_base + '/login',
      params= self.body
    )
    
    if req.status_code == 200:
      self.headers["Authorization"] = f"Bearer {req.json()['access_token']}"
      self.log.debug("Login executed with success")
      return
    self.log.error("Login ")
    self.register()

  
  def post(self, params):
    try:  
      req = requests.post(
        url=self.route_base + '/sysinfos',
        headers=self.headers, 
        json=params
      )
      self.log.debug("Post executed with success")
    except:
      self.log.error("Post can't be done")
      
      
  def logout(self):
    try:
      req = requests.get(
        url = self.route_base + '/logout',
        headers=self.headers
      )
      self.log.debug("Logout executed with success")
    except:
      self.log.error("Logout coulnd not be done")