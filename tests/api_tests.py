import requests
import logging
import sys
import yaml
from requests.structures import CaseInsensitiveDict
from pathlib import Path
from services.tools import Tools


class HandleRequests:

    def __init__(self, api_tests_login='api_tests_service', api_tests_password='api_tests_service'):
        tools = Tools()
        self.logger = tools.get_logger('api_tests')
        self.api_tests_settings = self.read_settings()
        self.api_tests_login = api_tests_login
        self.api_tests_password = api_tests_password
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
                self.logger.debug('register done')
                return True
            else:
                self.logger.debug(f'register failed! status code: {req.status_code}')
        except Exception as e:
            self.logger.exception('was not possible to register: {}'.format(repr(e)))

        return False

    def login(self) -> bool:
        url = self.base_url + "/api/account/login/"
        try:
            req = requests.post(url, json=self.login_body)
            if req.status_code == 200:
                self.headers["Authorization"] = f"Bearer {req.json()['token']}"
                self.logger.debug('login done')
                return True
            else:
                self.logger.debug(f'login failed! status code: {req.status_code}')
        except Exception as e:
            self.logger.exception('was not possible to login: {}'.format(repr(e)))

        return False

    def logout(self) -> bool:
        url = self.base_url + "/api/account/logout/"
        try:
            req = requests.get(url, headers=self.headers)
            if req.status_code == 200:
                self.logger.debug('logout done')
                return True
            else:
                self.logger.debug(f'logout failed! status code: {req.status_code}')
        except Exception as e:
            self.logger.exception('was not possible to logout: {}'.format(repr(e)))

        return False

    def get_users(self) -> dict:
        url = self.base_url + "/api/account/users/"
        try:
            req = requests.get(url, headers=self.headers)
            if req.status_code == 200:
                self.logger.debug('get users done')
                return req.json()
            else:
                self.logger.debug(f'get users failed! status code: {req.status_code}')
        except Exception as e:
            self.logger.exception('was not possible to get users: {}'.format(repr(e)))

        return None

    def get_user(self, id) -> dict:
        url = self.base_url + f"/api/account/user/{id}"
        try:
            req = requests.get(url, headers=self.headers)
            if req.status_code == 200:
                self.logger.debug('get user done')
                return req.json()
            else:
                self.logger.debug(f'get user failed! status code: {req.status_code}')
        except Exception as e:
            self.logger.exception('was not possible to get user: {}'.format(repr(e)))

        return None


if __name__ == '__main__':
    handle_requests = HandleRequests(api_tests_login='admin', api_tests_password='admin')
    #print(handle_requests.register())
    print(handle_requests.login())

    #print(handle_requests.get_users())
    print(handle_requests.get_user(id=1))
    print(handle_requests.logout())
