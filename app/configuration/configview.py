from app.main.mainview import base_event
import json
from flask import jsonify
from configuration import config
import errtypes

class configviewer(base_event):
    def __init__(self):
        super(configviewer, self).__init__()
        self.regist_event('event_query_web_port')
        pass

    def flask_recvdata(self, json_data):
        event = json_data['event']

        if 'event_query_web_port' == event:
            try:
                return jsonify({'code': errtypes.HttpResponseCode_Normal, 'msg': errtypes.HttpResponseMsg_Normal, 'http_port': config.HTTP_PORT,'websocket_port':config.WEBSOCKET_PORT})
            except Exception as e:
                return jsonify({'code': errtypes.HttpResponseCode_ServerError,'msg':str(e)})