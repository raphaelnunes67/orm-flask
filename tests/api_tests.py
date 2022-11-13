import requests
import logging
import sys
import yaml
from requests.structures import CaseInsensitiveDict
from pathlib import Path
from services.tools import Tools


class HandleRequests:

    def __init__(self):
        tools = Tools()
        self.logger = tools.get_logger('api_tests')
        self.api_tests_settings = self.read_settings()
        self.api_tests_login = 'api_tests_service'
        self.api_tests_password = 'api_tests_service'
        self.headers = CaseInsensitiveDict()
        self.headers["Content-Type"] = "application/json"
        self.login_body = {
            "login": self.api_tests_login,
            "password": self.api_tests_password
        }
        self.base_url = f"http://{self.api_tests_settings['host']}:{self.api_tests_settings['port']}"


    @staticmethod
    def read_settings() -> dict:

        with open(Path("..", "settings", "api_test_settings.yml")) as file:
            sync_settings = yaml.load(file, Loader=yaml.FullLoader)

        return sync_settings

    def register(self) -> bool:
        url = self.base_url + "/api/account/register/"
        try:
            req = requests.post(url, json=self.login_body)
            if req.status_code == 201:
                self.logger.debug('login in server done')
                return True
            else:
                self.logger.debug(f'register failed! status code: {req.status_code}')
        except Exception as e:
            self.logger.exception('was not possible to login in server: {}'.format(repr(e)))

        return False

    def login(self) -> bool:
        url = self.base_url + "/api/account/login/"
        try:
            req = requests.post(url, json=self.login_body)
            if req.status_code == 200:
                self.headers["Authorization"] = f"Bearer {req.json()['token']}"
                self.logger.debug('login in server done')
                return True
            else:
                self.logger.debug(f'login failed! status code: {req.status_code}')
        except Exception as e:
            self.logger.exception('was not possible to login in server: {}'.format(repr(e)))

        return False


if __name__ == '__main__':
    handle_requests = HandleRequests()
    print(handle_requests.register())
    print(handle_requests.login())


