# coding:utf-8

import os
from werkzeug.utils import secure_filename
import uuid

basedir = os.path.abspath(os.path.dirname(__file__))

class config:
    SECRET_KEY=str(uuid.uuid4())
    MAX_CONTENT_LENGTH=1024*1024*1024

    ROOTDIR='./website/'
    PATCHFOLDER = '/patch/'
    BLACKBOXFOLDER = '/blackbox/'
    BINFOLDER = '/bin/'
    TRANSMIT_BLOCK_SIZE = 32*1024
    SOCKET_PORT=5008
    HTTP_PORT=5010

    @staticmethod
    def init_app(app):
        pass

class development_config(config):
    DEBUG=True
    sqlite_database=''

class test_config(config):
    TESTING=True
    sqlite_database = ''

class produce_config(config):
    sqlite_database = ''

config_setting={
    'development':development_config,
    'test':test_config,
    'produce':produce_config,
    'default':development_config
}
