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
    BACKUPFILEDER='/backup/'
    TRANSMIT_BLOCK_SIZE = 32*1024
    WEB_PORT=5008
    HTTP_PORT=5010
    WEBSOCKET_PORT=5011

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

system_config = {
    #系统日志保留时间
    'retention_time_min':15*24*60,
    #检测时间间隔
    'time_intervel_sec':10*60,
    #检测路径
    'path_element':[
        {
            'path_root':config.ROOTDIR,
            'path_model':[
                # config.BLACKBOXFOLDER.strip('/')
            ]
        },
        {
            'path_root':'./pynsp/logs'
        }
        #config.ROOTDIR +config.BLACKBOXFOLDER
    ]
}

config_setting={
    'development':development_config,
    'test':test_config,
    'produce':produce_config,
    'default':development_config
}
