import logging
import logging.handlers
import os
import sys
import yaml
from pathlib import Path


class Tools:

    def __init__(self):

        self.logs_path = Path(os.path.dirname(__file__), '..', 'logs')
        if not os.path.exists(self.logs_path):
            os.mkdir(self.logs_path)

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

    def get_logger(self, logger_name):
        self.logger = logging.getLogger(logger_name)
        path = Path(self.logs_path, logger_name + '.log')
        file_handler = logging.handlers.RotatingFileHandler(filename=str(path),
                                                            mode='a',
                                                            maxBytes=10000000,
                                                            backupCount=10)
        formatter = logging.Formatter('[ %(asctime)s ] %(levelname)s %(message)s')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.DEBUG)
        return self.logger