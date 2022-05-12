#!/usr/bin/python
import logging
import logging.handlers
import os
import sys
import yaml

class Tools(object):
    def __init__(self):
        self.env = os.environ.get('DAMPER_SETTINGS', 'dev')
        self.logger = None
        if self.env == 'dev':
            self.logs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs'))
            self.settings_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'settings'))
        else:
            self.logs_path = os.path.abspath('/var/log/damper')
            self.settings_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'settings'))
        self._init_paths()

    def _init_paths(self):
        os.system('mkdir -p ' + self.logs_path)

    def __del__(self):
        pass

    def get_stdout_logger(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
        return self.logger

    def get_logger(self, path, logger_name):
        self.logger = logging.getLogger(logger_name)
        file_handler = logging.handlers.RotatingFileHandler(filename=str(path),
                                                            mode='a',
                                                            maxBytes=10000000,
                                                            backupCount=10)
        formatter = logging.Formatter('[ %(asctime)s ] %(levelname)s %(message)s')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.DEBUG)
        return self.logger

    def set_logger(self, log):
        self.logger = log

    def get_settings(self, file_path=None):
        if file_path:
            try:
                self.logger.info('trying to open file: {}'.format(file_path))
                with open(file_path, 'r') as raw_settings:
                    settings = yaml.load(raw_settings.read(), Loader=yaml.FullLoader)
                    self.logger.info('retrieve_device_info - dev_info: {}'.format(settings))
            except Exception as e:
                self.logger.error("get_settings:: error while opening file_path {}:{}".format(file_path, repr(e)))
            return settings

    @staticmethod
    def rounding_values(d, p):
        rounded_d = {}
        precision = "{0:.{}}", format(p)
        for k, v in d.items():
            v = float(precision.format(v))
            rounded_d[k] = v
        return rounded_d
