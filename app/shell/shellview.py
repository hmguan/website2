from app.main.mainview import base_event
import json
from flask import jsonify
from .shellmodel import *

class shellview(base_event):
    def __init__(self):
        super(shellview,self).__init__()
        self.regist_event('get_online_robot_list','get_offline_robot_list','get_unusual_robot_list',
                          'get_robot_detail_info','get_robot_system_info',
                          'get_robot_process_detail_info','query_user_transfer_queue','cancle_file_transform_task',
                          'query_robots_configuration_info','event_modify_file_lock','event_query_ftp_port',
                          'event_update_ntp_server','event_query_progress_info','event_operate_system_process',
                          'event_query_robot_process_list')
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
        elif 'query_user_transfer_queue' == event:
            return jsonify(query_transmit_queue(json_data.get('user_id'),json_data.get('file_type')))
        elif 'cancle_file_transform_task' == event:
            return jsonify(cancle_transform(json_data.get('user_id'),json_data.get('robot_id'),json_data.get('task_list')))
        elif 'query_robots_configuration_info' == event:
            return jsonify(get_on_line_robot_configuration(json_data.get('user_id')))
        elif 'event_modify_file_lock' == event:
            return jsonify(modify_file_lock(json_data.get('opcode'),json_data.get('robot_list')))
        elif 'event_query_ftp_port' == event:
            return jsonify(query_ftp_port())
        elif 'event_update_ntp_server' == event:
            return jsonify(update_robots_ntp_server(json_data.get('robot_list'),json_data.get('ntp_host')))
        elif 'event_query_progress_info' == event:
            return jsonify(query_robots_progress_info(json_data.get('user_id')))
        elif 'event_operate_system_process' ==event:
            return jsonify(operate_system_process(json_data.get('robot_list'),json_data.get('command')))
        elif 'event_query_robot_process_list' == event:
            return jsonify(query_robot_process_param_info(json_data.get('robot_id')))
        pass
