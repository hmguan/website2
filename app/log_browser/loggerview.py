from app.main.mainview import base_event
import json
from flask import jsonify
from .loggermodel import *

class loggerviewer(base_event):
    def __init__(self):
        super(loggerviewer, self).__init__()
        self.regist_event('write_logger_event')
        init_logger()
        pass

    def flask_recvdata(self, requst_obj):
        data = requst_obj.get_data()
        json_data = json.loads(data.decode('utf-8'))
        event = json_data['event']

        if 'write_logger_event' == event:
            return jsonify(write_browser_logger(json_data.get('data')))