# coding:utf-8

import os
from werkzeug.utils import secure_filename

basedir = os.path.abspath(os.path.dirname(__file__))

class config:
    SECRET_KEY='webserver!'
    MAX_CONTENT_LENGTH=1024*1024*1024

    ROOTDIR='/website/'
    PATCHFOLDER = '/patch/'
    BLACKBOXFOLDER = '/blackbox/'
    BINFOLDER = '/bin/'

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
