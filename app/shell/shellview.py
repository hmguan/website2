from app.main.mainview import base_event
import json
from flask import jsonify
from .shellmodel import *

class shellview(base_event):
    def __init__(self):
        super(shellview,self).__init__()
        self.regist_event('get_online_robot_list','get_offline_robot_list','get_unusual_robot_list',
                          'get_robot_detail_info','get_robot_system_info',
                          'get_robot_process_detail_info')
        pass

    def flask_recvdata(self,requst_obj):
        data = requst_obj.get_data()
        json_data = json.loads(data.decode('utf-8'))
        event = json_data['event']

        if 'get_online_robot_list' == event:
            return jsonify(get_online_robot_information(json_data.get('user_id')))
        elif 'get_offline_robot_list' == event:
            return jsonify(get_offline_robot_information())
        elif 'get_unusual_robot_list' == event:
            return jsonify(get_unusual_robot_information())
        elif 'get_robot_detail_info' == event:
            return jsonify(get_robot_detail_information(json_data.get('robot_id')))
        elif 'get_robot_system_info' == event:
            return jsonify(get_robot_system_information(json_data.get('robot_id')))
        elif 'get_robot_process_detail_info' == event:
            return jsonify(get_robot_process_detail_information(json_data.get('robot_id')))
        pass
