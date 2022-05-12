import requests
from time import sleep
from datetime import datetime
from datetime import timedelta
from random import seed
import json
from random import randint


serial_base = 'XPTO2021-'

initial_date = '2021-10-05T17:36:40'
final_date = '2021-10-10T17:36:40'

if __name__ == '__main__':
    initial_datetime = datetime.fromisoformat(initial_date)
    final_datetime = datetime.fromisoformat(final_date)

    for d in range((final_datetime - initial_datetime).days):
        for _ in range(5):
            s = randint(0, 86400)
            dut = randint(0, 99)
            current_date = initial_datetime + timedelta(days=d, seconds=s)
            payload = dict(serial=serial_base + str(dut).zfill(2), details=json.dumps(details))
            # req = requests.post(url='http://127.0.0.1:5000/api/dutinfo/',
            #                     params={'serial': serial_base + str(dut).zfill(2),
            #                             'details': json.dumps(details),
            #                             'timestamp': current_date})
            print('datetime: {}, serial: {}{}'.format(current_date, serial_base, str(dut).zfill(2)))
