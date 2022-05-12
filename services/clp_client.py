from requests.structures import CaseInsensitiveDict
from time import sleep
from datetime import datetime, timedelta
from random import randint
import requests, yaml, logging

def read_route_base():
    """
    Read route base to publish data.

    :return: Route base path.
    :rtype: String
    """

    with open('../settings/clp_monitor.yml') as file:
      clp_monitor = yaml.load(file, Loader=yaml.FullLoader)
      route_base = clp_monitor['api']['host'] + ':' + str(clp_monitor['api']['port'])
      route_base = route_base + clp_monitor['api']['route']
    return route_base

class PlcMonitor:
  """
  This is a class to perform a data insert client. This class is responsible to
  execute operations like, login, post e logout.

  """
  def __init__(self):

    self.route_base = read_route_base()
    self.plc_login = 'clp_client'
    self.plc_password = 'clp_client'
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
      url = self.route_base + '/account/register',
      params= self.body
    )

    self.login()


  def login(self):
    req = requests.post(
      url = self.route_base + '/account/login',
      params= self.body
    )

    if req.status_code == 200:
      self.headers["Authorization"] = f"Bearer {req.json()['access_token']}"
      self.log.debug("Login executed with success")
      return
    self.log.error("Login can't be done")
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
        url = self.route_base + '/account/logout',
        headers=self.headers
      )
      self.log.debug("Logout executed with success")
    except:
      self.log.error("Logout can't be done")

  @staticmethod
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
  

if __name__== '__main__':

  PlcMonitor.configure_log()

  plc = PlcMonitor()
  base = datetime.today()
  total_days = 230
  date_list = [base + timedelta(days=x) for x in range(total_days)] # x dias a partir de hj
  for n in range(total_days):
    plc.login()
    s = randint(0, 86400)
    params = {
      "model": "XYZ-ABC" +  str(randint(0,99)).zfill(3),
      "quantity": randint(100, 100000),
      "work_order": "DAMPER"+str(randint(0,9999)).zfill(4)+"-TEST",
      "created_at": date_list[n].isoformat(),
      "details": "Some text for test"
    }
    print(params['created_at'])
    plc.post(params)
    plc.logout()